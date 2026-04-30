from __future__ import annotations

import json
import logging
import time
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import requests

from config import GRAVEYARD_FOLDER, MAX_ISSUES_PER_REPO


logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
LOGGER = logging.getLogger(__name__)


@dataclass(slots=True)
class Issue:
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
