from __future__ import annotations

import json
import logging
import os
import re
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
    SCAN_PAGES_PER_REPO,
    REPO_ROTATION_COOLDOWN_DAYS,
    STATS_FOLDER,
)


logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
LOGGER = logging.getLogger(__name__)
MAX_BODY_LENGTH = 3000
SECONDS_BETWEEN_REPOS = 2
MAX_COMMENTS_TO_INSPECT = 12

# Minimum upvotes (reactions +1) for an issue to be considered
MIN_REACTIONS = MIN_UPVOTES  # from config
# If reactions >= this, skip label check entirely
HIGH_REACTIONS_OVERRIDE = HIGH_DEMAND_UPVOTES_OVERRIDE  # from config

# File that tracks last-used date per repo slug
REPO_ROTATION_FILE = Path(STATS_FOLDER) / "repo_rotation.json"

# Labels that indicate an issue is already resolved / closed-as-done
RESOLVED_LABELS = {
    "completed", "done", "duplicate", "fixed", "implemented",
    "released", "resolved", "wontfix",
}

# GitHub state_reason values that mean the issue was intentionally closed as done.
# "not_planned" means abandoned/wontfix — we still want those.
# "completed" means the issue was actually resolved and should be skipped.
RESOLVED_STATE_REASONS = {"completed", "duplicate"}

# Text patterns that signal the issue is already solved in practice
RESOLVED_TEXT_PATTERNS = [
    re.compile(pattern, re.IGNORECASE) for pattern in [
        r"\balready (?:available|implemented|supported|possible|works?|added)\b",
        r"\bthis (?:is|was) (?:already )?(?:available|implemented|supported|fixed|done)\b",
        r"\b(?:fixed|resolved|implemented|released|shipped) (?:in|by|since|with)\b",
        r"\bduplicate of\b",
        r"\byou can already\b",
        r"\buse (?:the )?.+ instead\b",
        r"\bavailable (?:in|via|through|as of)\b",
        r"\bpackaged (?:for|in|on)\b",
        r"\bhomebrew\b",
        r"\bapt(?:-get)? install\b",
        r"\bwinget install\b",
        r"\bpacman -S\b",
        r"\bscoop install\b",
        r"\bchoco install\b",
        r"\bsnapcraft\b",
        r"\bflatpak install\b",
        r"\bclosing (?:as|this as) (?:resolved|done|fixed|duplicate|complete)\b",
        r"\bhas been (?:added|merged|implemented|shipped|released)\b",
    ]
]


# ---------------------------------------------------------------------------
# Repo rotation helpers
# ---------------------------------------------------------------------------

def _load_rotation() -> dict[str, str]:
    """Load {repo_slug: last_used_date_iso} from disk."""
    if not REPO_ROTATION_FILE.exists():
        return {}
    try:
        data = json.loads(REPO_ROTATION_FILE.read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else {}
    except (json.JSONDecodeError, OSError):
        return {}


def _save_rotation(rotation: dict[str, str]) -> None:
    REPO_ROTATION_FILE.parent.mkdir(parents=True, exist_ok=True)
    REPO_ROTATION_FILE.write_text(
        json.dumps(rotation, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )


def _days_since_iso(date_iso: str) -> float:
    try:
        dt = datetime.fromisoformat(date_iso)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return (datetime.now(timezone.utc) - dt).total_seconds() / 86400
    except ValueError:
        return float("inf")


def is_repo_on_cooldown(repo: str, rotation: dict[str, str]) -> bool:
    """Return True if this repo was used too recently."""
    last_used = rotation.get(repo)
    if not last_used:
        return False
    days = _days_since_iso(last_used)
    on_cooldown = days < REPO_ROTATION_COOLDOWN_DAYS
    if on_cooldown:
        LOGGER.info(
            "[Rotation] Skipping %s — used %.1f days ago (cooldown=%d days).",
            repo, days, REPO_ROTATION_COOLDOWN_DAYS,
        )
    return on_cooldown


def mark_repo_used(repo: str) -> None:
    """Record today as the last-used date for this repo."""
    rotation = _load_rotation()
    rotation[repo] = datetime.now(timezone.utc).isoformat()
    _save_rotation(rotation)
    LOGGER.info("[Rotation] Marked %s as used today.", repo)


# ---------------------------------------------------------------------------
# Graveyard helpers
# ---------------------------------------------------------------------------

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
        return []
    LOGGER.info("Loaded %d existing issues for %s.", len(data), repo)
    return data


def save_graveyard(repo: str, issues: list[dict[str, Any]]) -> None:
    path = _graveyard_path(repo)
    path.parent.mkdir(parents=True, exist_ok=True)
    sorted_issues = sorted(issues, key=lambda item: int(item.get("reactions", 0)), reverse=True)

    serializable: list[dict[str, Any]] = []
    for issue in sorted_issues:
        try:
            serializable.append(asdict(GraveyardEntry(**issue)))
        except (TypeError, KeyError):
            # Already a plain dict with extra/missing fields — keep as-is
            serializable.append(issue)

    with path.open("w", encoding="utf-8") as handle:
        json.dump(serializable, handle, indent=2, ensure_ascii=False)
    LOGGER.info("Saved %d issues to %s.", len(serializable), path)


def mark_resurrected(repo: str, issue_number: int) -> None:
    """Set already_resurrected=True for the given issue in the graveyard."""
    issues = load_graveyard(repo)
    updated = False
    for issue in issues:
        if int(issue.get("issue_number", -1)) == issue_number:
            issue["already_resurrected"] = True
            updated = True
            LOGGER.info("Marked issue #%d as resurrected in %s graveyard.", issue_number, repo)
            break
    if updated:
        save_graveyard(repo, issues)
    else:
        LOGGER.warning(
            "Could not find issue #%d in graveyard for %s to mark as resurrected.",
            issue_number,
            repo,
        )


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
            time.sleep(2 ** attempt)
            continue

        if response.status_code == 429:
            retry_after = int(response.headers.get("Retry-After", 60))
            LOGGER.warning("Rate limit (429) for %s. Waiting %ss.", url, retry_after)
            time.sleep(retry_after)
            continue

        if response.status_code >= 500:
            if attempt == max_attempts - 1:
                LOGGER.error("GitHub server error %s after retries for %s.", response.status_code, url)
                return None
            time.sleep(2 ** attempt)
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

    while page <= SCAN_PAGES_PER_REPO and len(all_issues) < MAX_ISSUES_PER_REPO:
        params = {
            "state": "closed",           # focus on closed issues — abandoned features live here
            "per_page": per_page,
            "page": page,
            "sort": "reactions",         # most-reacted first = highest impact candidates
            "direction": "desc",         # highest reactions at the top
        }
        response = _request_with_backoff(url, headers=headers, params=params)
        if response is None:
            break

        if response.status_code == 404:
            LOGGER.error("Repository not found: %s", repo)
            return []

        if response.status_code == 403:
            LOGGER.warning("Rate limit (403) for %s. Waiting 60s.", repo)
            time.sleep(60)
            response = _request_with_backoff(url, headers=headers, params=params, max_attempts=1)
            if response is None or response.status_code == 403:
                LOGGER.error("Rate limit retry failed for %s.", repo)
                return all_issues

        if response.status_code != 200:
            LOGGER.error("Failed to fetch issues for %s. HTTP %s", repo, response.status_code)
            return all_issues

        try:
            page_issues = response.json()
        except ValueError:
            LOGGER.error("Failed to decode JSON for %s page %d.", repo, page)
            return all_issues

        if not isinstance(page_issues, list) or not page_issues:
            break

        remaining = MAX_ISSUES_PER_REPO - len(all_issues)
        all_issues.extend(page_issues[:remaining])
        LOGGER.info("Fetched %d issues from %s page %d.", len(page_issues), repo, page)
        page += 1

    return all_issues[:MAX_ISSUES_PER_REPO]


def get_issue_comments(repo: str, issue_number: int, token: str) -> list[dict[str, Any]]:
    """Fetch the first MAX_COMMENTS_TO_INSPECT comments for a given issue."""
    url = f"https://api.github.com/repos/{repo}/issues/{issue_number}/comments"
    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {token}",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    response = _request_with_backoff(
        url, headers=headers, params={"per_page": MAX_COMMENTS_TO_INSPECT}
    )
    if response is None or response.status_code != 200:
        return []
    try:
        data = response.json()
    except ValueError:
        return []
    return data if isinstance(data, list) else []


def _has_resolved_label(issue: dict[str, Any]) -> bool:
    labels = issue.get("labels", [])
    label_names = {
        str(label.get("name", "")).strip().lower()
        for label in labels
        if isinstance(label, dict)
    }
    return any(label in RESOLVED_LABELS for label in label_names)


def _has_resolved_signal(text: str) -> bool:
    """Return True if the text contains language suggesting the issue is solved."""
    compact = re.sub(r"\s+", " ", text).strip()
    if not compact:
        return False
    return any(pattern.search(compact) for pattern in RESOLVED_TEXT_PATTERNS)


def _is_closed_via_pr(issue: dict[str, Any]) -> bool:
    """
    Return True if this issue was closed by a linked pull request.

    The GitHub REST API attaches a 'pull_request' key to an issue object
    when it was closed via a PR. This is the most reliable signal that
    the feature/bug was actually implemented — no extra API call needed.

    Note: the presence of 'pull_request' alone means a PR was linked.
    We do NOT require merged_at to be non-null here because:
    - The issues endpoint returns closed issues (state=closed).
    - A closed issue with a linked PR almost always means merged.
    - Checking merged_at would require a separate PR API call per issue.
    """
    pr_data = issue.get("pull_request")
    if not pr_data or not isinstance(pr_data, dict):
        return False
    # If merged_at is present in the payload (sometimes it is), use it directly.
    merged_at = pr_data.get("merged_at")
    if merged_at is not None:
        # merged_at is a timestamp string if merged, or null if not
        return bool(merged_at)
    # merged_at not present in payload — existence of pull_request key on a
    # closed issue is a strong enough signal.
    return True


def _is_closed_as_completed(issue: dict[str, Any]) -> bool:
    """
    Return True if GitHub's state_reason for this issue is 'completed' or 'duplicate'.

    state_reason is set by whoever closed the issue:
      - 'completed'  → the work is done, issue is resolved
      - 'not_planned' → abandoned/wontfix — we still want these
      - 'duplicate'  → resolved via another issue
      - None         → old issues closed before state_reason was introduced (2022)
    """
    state_reason = str(issue.get("state_reason") or "").strip().lower()
    return state_reason in RESOLVED_STATE_REASONS


def is_already_solved(repo: str, issue: dict[str, Any], token: str) -> bool:
    """
    Return True if the issue appears to be already solved / obsolete.

    Checks (in order, cheapest first — no extra API calls for checks 0-2):
      0. Issue has a linked pull_request field → closed via merged PR → solved.
      0b. GitHub state_reason is 'completed' or 'duplicate' → solved.
      1. Label contains a resolved signal.
      2. Title or body contains a resolved text pattern.
      3. Any of the first MAX_COMMENTS_TO_INSPECT comments contains a resolved pattern
         (one API call).
    """
    # Check 0: closed via a linked PR (free — data already in issue object)
    if _is_closed_via_pr(issue):
        LOGGER.debug(
            "[SolvedCheck] %s#%s: closed via linked PR — skipping.",
            repo, issue.get("number"),
        )
        return True

    # Check 0b: GitHub state_reason signals completion (free — data already in issue object)
    if _is_closed_as_completed(issue):
        LOGGER.debug(
            "[SolvedCheck] %s#%s: state_reason=%s — skipping.",
            repo, issue.get("number"), issue.get("state_reason"),
        )
        return True

    # Check 1: resolved label (free — data already in issue object)
    if _has_resolved_label(issue):
        return True

    # Check 2: resolved signal in title or body (free — data already in issue object)
    title = str(issue.get("title", ""))
    body = str(issue.get("body") or "")
    if _has_resolved_signal(title) or _has_resolved_signal(body):
        return True

    # Check 3: scan comments (one API call per issue — only reached if all above pass)
    comments = get_issue_comments(repo, int(issue.get("number", 0)), token)
    for comment in comments:
        comment_body = str(comment.get("body") or "")
        if _has_resolved_signal(comment_body):
            return True

    return False


def _get_reactions_count(issue: dict[str, Any]) -> int:
    reactions = issue.get("reactions")
    if isinstance(reactions, dict):
        plus_one = int(reactions.get("+1", 0))
        heart = int(reactions.get("heart", 0))
        hooray = int(reactions.get("hooray", 0))
        rocket = int(reactions.get("rocket", 0))
        if plus_one > 0 or heart > 0 or hooray > 0 or rocket > 0:
            return plus_one + heart + hooray + rocket
        # Some older issues may only have total_count
        return int(reactions.get("total_count", 0))
    return 0


def is_abandoned(issue: dict[str, Any]) -> bool:
    """Determine if a GitHub issue qualifies as abandoned and worth resurrecting.

    Rules (in order):
    1. Skip pull requests.
    2. Must have >= MIN_REACTIONS upvotes.
    3. Must be closed OR last updated >= MONTHS_STALE_THRESHOLD months ago.
    4. If reactions >= HIGH_REACTIONS_OVERRIDE, always qualifies (ignore labels).
    5. Otherwise must have at least one label from ABANDONED_LABELS (from config).
    """
    # 1. Skip PRs
    if "pull_request" in issue:
        return False

    # 2. Upvote threshold
    reactions = _get_reactions_count(issue)
    if reactions < MIN_REACTIONS:
        return False

    # 3. Must be stale or closed
    updated_at = str(issue.get("updated_at", ""))
    is_closed = str(issue.get("state", "")).lower() == "closed"
    try:
        stale_enough = months_since(updated_at) >= MONTHS_STALE_THRESHOLD if updated_at else False
    except ValueError:
        LOGGER.warning("Invalid updated_at on issue #%s; skipping.", issue.get("number"))
        return False

    if not (is_closed or stale_enough):
        return False

    # 4. High-demand override: skip label check
    if reactions >= HIGH_REACTIONS_OVERRIDE:
        return True

    # 5. Must have at least one qualifying label (sourced from config.ABANDONED_LABELS)
    labels = issue.get("labels", [])
    label_names = {
        str(label.get("name", "")).strip().lower()
        for label in labels
        if isinstance(label, dict)
    }
    return any(label in ABANDONED_LABELS for label in label_names)


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
        reactions=_get_reactions_count(issue),
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
        # Skip issues that appear to already be solved in practice
        if is_already_solved(repo, raw_issue, token):
            LOGGER.info("Skipping solved/obsolete issue: %s#%d", repo, issue_number)
            continue
        entry = _entry_from_issue(repo, raw_issue)
        new_entries.append(asdict(entry))
        LOGGER.info("Qualified issue found: %s#%d (reactions=%d)", repo, issue_number, entry.reactions)

    if new_entries:
        save_graveyard(repo, existing + new_entries)
        LOGGER.info("%s: %d new issues added to graveyard", repo, len(new_entries))
    else:
        LOGGER.info("No new qualifying issues for %s.", repo)

    return len(new_entries)


def _timestamp() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def scan_issues() -> None:
    """
    Scan repos for abandoned issues, skipping any repo that was recently used
    (within REPO_ROTATION_COOLDOWN_DAYS). This prevents the same repo from
    being picked every single day.
    """
    import os
    token = os.environ.get("GITHUB_TOKEN", "")
    rotation = _load_rotation()

    skipped = 0
    for repo in REPOS_TO_SCAN:
        if is_repo_on_cooldown(repo, rotation):
            skipped += 1
            continue
        try:
            scan_repo(repo, token)
        except Exception as error:
            LOGGER.error("Unexpected error scanning %s: %s", repo, error)
        time.sleep(SECONDS_BETWEEN_REPOS)

    if skipped:
        LOGGER.info("[Rotation] %d repo(s) skipped due to cooldown.", skipped)


def main() -> None:
    from dotenv import load_dotenv
    load_dotenv()
    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        raise EnvironmentError("GITHUB_TOKEN not set")

    rotation = _load_rotation()
    total = 0
    for index, repo in enumerate(REPOS_TO_SCAN):
        if is_repo_on_cooldown(repo, rotation):
            print(f"[{_timestamp()}] Skipping {repo} (cooldown)")
            continue
        print(f"[{_timestamp()}] Scanning {repo}...")
        try:
            added = scan_repo(repo, token)
        except Exception as error:
            LOGGER.error("Error scanning %s: %s", repo, error)
            added = 0
        total += added
        print(f"[{_timestamp()}] {repo}: {added} new issues added to graveyard")
        if index < len(REPOS_TO_SCAN) - 1:
            time.sleep(SECONDS_BETWEEN_REPOS)

    print(f"\u2705 Scan complete. Total new issues found: {total}")


if __name__ == "__main__":
    main()
