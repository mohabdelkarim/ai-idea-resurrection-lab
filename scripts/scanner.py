from __future__ import annotations

import json
import logging
import os
import time
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import requests

from config import (
    ABANDONED_LABELS,
    GRAVEYARD_FOLDER,
    HIGH_DEMAND_UPVOTES_OVERRIDE,
    MAX_ISSUES_PER_REPO,
    MIN_UPVOTES,
    MONTHS_STALE_THRESHOLD,
    REPOS_TO_SCAN,
)


logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
LOGGER = logging.getLogger(__name__)
MAX_BODY_LENGTH = 3000
SECONDS_BETWEEN_REPOS = 2


@dataclass(slots=True)
class GraveyardEntry:
    repo: str
    issue_number: int
    title: str
    body: str
    reactions: int
    created_at: str
    updated_at: str
    labels: list[str]
    url: str
    html_url: str
    author_login: str
    author_profile: str
    already_resurrected: bool = False


def months_since(date_str: str) -> float:
    parsed = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    delta_days = (datetime.now(timezone.utc) - parsed).total_seconds() / 86400
    return delta_days / 30.4375


def _sanitize_repo_name(repo: str) -> str:
    return repo.replace("/", "__")


def _graveyard_path(repo: str) -> Path:
    return Path(GRAVEYARD_FOLDER) / f"{_sanitize_repo_name(repo)}.json"


def load_graveyard(repo: str) -> list[dict[str, Any]]:
    path = _graveyard_path(repo)
    if not path.exists():
        LOGGER.info("No graveyard file found for %s, starting fresh.", repo)
        return []

    try:
        with path.open("r", encoding="utf-8") as handle:
            data = json.load(handle)
    except json.JSONDecodeError:
        LOGGER.warning("Invalid JSON in %s; resetting graveyard data.", path)
        return []

    if not isinstance(data, list):
        LOGGER.warning("Unexpected data format in %s; expected JSON array.", path)
        return []

    LOGGER.info("Loaded %d existing issues for %s.", len(data), repo)
    return data


def save_graveyard(repo: str, issues: list[dict[str, Any]]) -> None:
    path = _graveyard_path(repo)
    path.parent.mkdir(parents=True, exist_ok=True)
    sorted_issues = sorted(issues, key=lambda item: int(item.get("reactions", 0)), reverse=True)
    serializable = [asdict(GraveyardEntry(**issue)) for issue in sorted_issues]

    with path.open("w", encoding="utf-8") as handle:
        json.dump(serializable, handle, indent=2, ensure_ascii=False)

    LOGGER.info("Saved %d issues to %s.", len(serializable), path)


def _request_with_backoff(
    url: str,
    headers: dict[str, str],
    params: dict[str, Any],
    max_attempts: int = 3,
) -> requests.Response | None:
    for attempt in range(max_attempts):
        try:
            response = requests.get(url, headers=headers, params=params, timeout=30)
        except requests.RequestException as error:
            if attempt == max_attempts - 1:
                LOGGER.error("Network error after retries for %s: %s", url, error)
                return None
            backoff = 2**attempt
            LOGGER.warning("Network error for %s. Retrying in %ss.", url, backoff)
            time.sleep(backoff)
            continue

        if response.status_code >= 500:
            if attempt == max_attempts - 1:
                LOGGER.error(
                    "GitHub server error %s after retries for %s.",
                    response.status_code,
                    url,
                )
                return None
            backoff = 2**attempt
            LOGGER.warning(
                "GitHub server error %s for %s. Retrying in %ss.",
                response.status_code,
                url,
                backoff,
            )
            time.sleep(backoff)
            continue

        return response
    return None


def get_repo_issues(repo: str, token: str) -> list[dict[str, Any]]:
    url = f"https://api.github.com/repos/{repo}/issues"
    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {token}",
        "X-GitHub-Api-Version": "2022-11-28",
    }

    page = 1
    all_issues: list[dict[str, Any]] = []
    per_page = min(100, MAX_ISSUES_PER_REPO)

    while len(all_issues) < MAX_ISSUES_PER_REPO:
        params = {"state": "all", "per_page": per_page, "page": page}
        response = _request_with_backoff(url, headers=headers, params=params)
        if response is None:
            break

        if response.status_code == 404:
            LOGGER.error("Repository not found: %s", repo)
            return []

        if response.status_code == 403:
            LOGGER.warning("Rate limit hit while scanning %s. Waiting 60 seconds.", repo)
            time.sleep(60)
            response = _request_with_backoff(url, headers=headers, params=params, max_attempts=1)
            if response is None or response.status_code == 403:
                LOGGER.error("Rate limit retry failed for %s. Skipping repository.", repo)
                return all_issues

        if response.status_code != 200:
            LOGGER.error(
                "Failed to fetch issues for %s. HTTP %s: %s",
                repo,
                response.status_code,
                response.text[:300],
            )
            return all_issues

        try:
            page_issues = response.json()
        except ValueError:
            LOGGER.error("Failed to decode JSON response for %s page %d.", repo, page)
            return all_issues

        if not isinstance(page_issues, list) or not page_issues:
            break

        remaining = MAX_ISSUES_PER_REPO - len(all_issues)
        all_issues.extend(page_issues[:remaining])
        LOGGER.info("Fetched %d issues from %s page %d.", len(page_issues), repo, page)
        page += 1

    return all_issues[:MAX_ISSUES_PER_REPO]


def is_abandoned(issue: dict[str, Any]) -> bool:
    if "pull_request" in issue:
        return False

    reactions = int(issue.get("reactions", {}).get("+1", 0))
    if reactions < MIN_UPVOTES:
        return False

    updated_at = str(issue.get("updated_at", ""))
    is_closed = str(issue.get("state", "")).lower() == "closed"
    try:
        stale_enough = months_since(updated_at) >= MONTHS_STALE_THRESHOLD if updated_at else False
    except ValueError:
        LOGGER.warning("Invalid updated_at on issue #%s; skipping.", issue.get("number"))
        return False
    if not (is_closed or stale_enough):
        return False

    labels = issue.get("labels", [])
    label_names = {
        str(label.get("name", "")).strip().lower()
        for label in labels
        if isinstance(label, dict)
    }
    has_matching_label = any(label in ABANDONED_LABELS for label in label_names)
    return reactions >= HIGH_DEMAND_UPVOTES_OVERRIDE or has_matching_label


def _entry_from_issue(repo: str, issue: dict[str, Any]) -> GraveyardEntry:
    author_login = str(issue.get("user", {}).get("login", "unknown"))
    body = str(issue.get("body") or "")[:MAX_BODY_LENGTH]
    labels = [
        str(label.get("name", ""))
        for label in issue.get("labels", [])
        if isinstance(label, dict)
    ]
    return GraveyardEntry(
        repo=repo,
        issue_number=int(issue.get("number", 0)),
        title=str(issue.get("title", "")),
        body=body,
        reactions=int(issue.get("reactions", {}).get("+1", 0)),
        created_at=str(issue.get("created_at", "")),
        updated_at=str(issue.get("updated_at", "")),
        labels=labels,
        url=str(issue.get("url", "")),
        html_url=str(issue.get("html_url", "")),
        author_login=author_login,
        author_profile=f"https://github.com/{author_login}",
        already_resurrected=False,
    )


def scan_repo(repo: str, token: str) -> int:
    LOGGER.info("Scanning %s...", repo)
    existing = load_graveyard(repo)
    existing_issue_numbers = {
        int(item.get("issue_number", 0))
        for item in existing
        if isinstance(item, dict) and "issue_number" in item
    }

    raw_issues = get_repo_issues(repo, token)
    new_entries: list[dict[str, Any]] = []

    for raw_issue in raw_issues:
        issue_number = int(raw_issue.get("number", 0))
        if issue_number in existing_issue_numbers:
            continue
        if not is_abandoned(raw_issue):
            continue

        entry = _entry_from_issue(repo, raw_issue)
        new_entries.append(asdict(entry))
        LOGGER.info("Qualified issue found: %s#%d", repo, issue_number)

    if new_entries:
        save_graveyard(repo, existing + new_entries)
    else:
        LOGGER.info("No new qualifying issues for %s.", repo)

    LOGGER.info("%s: %d new issues added to graveyard", repo, len(new_entries))
    return len(new_entries)


def _timestamp() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def main() -> None:
    from dotenv import load_dotenv

    load_dotenv()
    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        raise EnvironmentError("GITHUB_TOKEN not set in .env")

    total_new_issues = 0
    for index, repo in enumerate(REPOS_TO_SCAN):
        print(f"[{_timestamp()}] Scanning {repo}...")
        try:
            added = scan_repo(repo, token)
        except Exception as error:  # Defensive fallback to keep batch scan running.
            LOGGER.error("Unexpected error while scanning %s: %s", repo, error)
            added = 0

        total_new_issues += added
        print(f"[{_timestamp()}] {repo}: {added} new issues added to graveyard")

        if index < len(REPOS_TO_SCAN) - 1:
            time.sleep(SECONDS_BETWEEN_REPOS)

    print(f"✅ Scan complete. Total new issues found: {total_new_issues}")


if __name__ == "__main__":
    main()

def scan_issues() -> None:
    import os

    token = os.environ.get("GITHUB_TOKEN", "")
    for repo in REPOS_TO_SCAN:
        scan_repo(repo, token)
