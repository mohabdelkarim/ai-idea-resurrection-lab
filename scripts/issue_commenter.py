"""issue_commenter.py

Posts a polite, informative comment on the original GitHub issue
after a resurrection. This drives organic traffic back to the lab
because everyone who 👍'd the issue gets a GitHub notification.

Rules:
- Only posts once per issue (checks for existing bot comment first).
- Respects the GitHub API rate limit.
- Comment is concise, respectful, and adds clear value.
- Never claims "working code" unless meta.poc_validated is true.
"""
from __future__ import annotations

import logging
import time
from typing import Any

import requests

LOGGER = logging.getLogger(__name__)
BOT_COMMENT_MARKER = "<!-- resurrection-bot-comment -->"
LAB_URL = "https://github.com/mohabdelkarim/ai-idea-resurrection-lab"


def _github_headers(token: str) -> dict[str, str]:
    return {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {token}",
        "X-GitHub-Api-Version": "2022-11-28",
    }


def _get_existing_comments(repo: str, issue_number: int, token: str) -> list[dict[str, Any]]:
    url = f"https://api.github.com/repos/{repo}/issues/{issue_number}/comments"
    headers = _github_headers(token)
    all_comments: list[dict[str, Any]] = []
    page = 1
    while True:
        response = requests.get(
            url, headers=headers, params={"per_page": 100, "page": page}, timeout=20
        )
        if response.status_code != 200:
            LOGGER.warning(
                "[Commenter] Could not fetch comments for %s#%d: HTTP %s",
                repo, issue_number, response.status_code,
            )
            return []
        data = response.json()
        if not isinstance(data, list) or not data:
            break
        all_comments.extend(data)
        if len(data) < 100:
            break
        page += 1
    return all_comments


def _already_commented(comments: list[dict[str, Any]]) -> bool:
    for comment in comments:
        body = str(comment.get("body", ""))
        if BOT_COMMENT_MARKER in body:
            return True
    return False


def _resurrection_url(meta: dict[str, Any]) -> str:
    slug = str(meta.get("resurrection_slug", "")).strip()
    if slug:
        return f"{LAB_URL}/tree/main/resurrections/{slug}"
    date = str(meta.get("date", "")).strip()
    repo = str(meta.get("repo", "")).strip().replace("/", "-").replace(".", "-")
    issue_number = int(meta.get("issue_number", 0))
    if date and repo and issue_number:
        return f"{LAB_URL}/tree/main/resurrections/{date}_{repo}_{issue_number}"
    return LAB_URL


def _poc_note(meta: dict[str, Any]) -> str:
    has_poc = bool(meta.get("has_poc", False))
    poc_validated = bool(meta.get("poc_validated", False))
    poc_language = str(meta.get("poc_language", "")).strip() or "code"

    if has_poc and poc_validated:
        return f"There's also a small `{poc_language}` sketch in the write-up (rough, not a real patch)."
    if has_poc:
        return f"There's a draft `{poc_language}` sketch too. Treat it as notes, not something to merge."
    return "No code sketch this time, just the write-up."


def _clean_prose(text: str) -> str:
    """Drop separator dashes from comment prose (keep hyphens inside words/URLs)."""
    cleaned = str(text or "")
    for sep in (" — ", " – ", " - ", "—", "–"):
        cleaned = cleaned.replace(sep, ", " if sep.strip() else ", ")
    cleaned = cleaned.replace(" ,", ",")
    return " ".join(cleaned.split()).strip()


def _build_comment(meta: dict[str, Any]) -> str:
    effort_hours = meta.get("effort_hours", "?")
    try:
        effort_display = str(int(float(effort_hours)))
    except (TypeError, ValueError):
        effort_display = str(effort_hours)

    summary = _clean_prose(str(meta.get("one_line_summary", "")))
    why = _clean_prose(str(meta.get("one_line_why", "")))
    resurrection_url = _resurrection_url(meta)

    bits: list[str] = [
        BOT_COMMENT_MARKER,
        "",
        f"Hey, I dug back into this idea and wrote up a short note here: "
        f"[analysis]({resurrection_url}).",
        "",
    ]

    if summary:
        bits.append(summary)
        bits.append("")
    if why:
        bits.append(why)
        bits.append("")

    bits.append(_poc_note(meta))
    bits.append("")
    bits.append(
        f"Rough effort guess from the write-up: about {effort_display} hours. "
        "Not affiliated with this project, just sharing in case it's useful."
    )

    return "\n".join(bits) + "\n"


def post_resurrection_comment(meta: dict[str, Any], token: str, dry_run: bool = False) -> dict[str, Any]:
    from config import POST_ORIGINAL_ISSUE_COMMENT

    if not POST_ORIGINAL_ISSUE_COMMENT:
        LOGGER.info("[Commenter] Disabled via config. Skipping.")
        return {
            "attempted": False,
            "posted": False,
            "status": "disabled",
            "comment_url": "",
        }

    if not token.strip():
        LOGGER.warning(
            "[Commenter] No COMMENT_GITHUB_TOKEN (or fallback token) set — "
            "cross-repo comments are disabled."
        )
        return {
            "attempted": False,
            "posted": False,
            "status": "missing_token",
            "comment_url": "",
        }

    repo = str(meta.get("repo", ""))
    issue_number = int(meta.get("issue_number", 0))
    if not repo or not issue_number:
        LOGGER.warning("[Commenter] Missing repo or issue_number in meta. Skipping.")
        return {
            "attempted": False,
            "posted": False,
            "status": "missing_meta",
            "comment_url": "",
        }

    existing_comments = _get_existing_comments(repo, issue_number, token)
    if _already_commented(existing_comments):
        LOGGER.info("[Commenter] Already commented on %s#%d. Skipping.", repo, issue_number)
        return {
            "attempted": True,
            "posted": False,
            "status": "already_commented",
            "comment_url": "",
        }

    comment_body = _build_comment(meta)
    if dry_run:
        LOGGER.info("[Commenter] DRY RUN — would post:\n%s", comment_body)
        return {
            "attempted": True,
            "posted": True,
            "status": "dry_run",
            "comment_url": "",
        }

    url = f"https://api.github.com/repos/{repo}/issues/{issue_number}/comments"
    headers = _github_headers(token)
    time.sleep(1)
    response = requests.post(url, headers=headers, json={"body": comment_body}, timeout=20)

    if response.status_code == 201:
        try:
            payload = response.json()
        except ValueError:
            payload = {}
        LOGGER.info("[Commenter] Comment posted on %s#%d", repo, issue_number)
        return {
            "attempted": True,
            "posted": True,
            "status": "posted",
            "comment_url": str(payload.get("html_url", "")),
        }
    if response.status_code == 403:
        LOGGER.warning(
            "[Commenter] Cannot comment on %s#%d: permission denied or locked issue.",
            repo, issue_number,
        )
        return {
            "attempted": True,
            "posted": False,
            "status": "forbidden_or_locked",
            "comment_url": "",
        }
    if response.status_code == 404:
        LOGGER.warning("[Commenter] Issue %s#%d not found or no access.", repo, issue_number)
        return {
            "attempted": True,
            "posted": False,
            "status": "not_found",
            "comment_url": "",
        }

    LOGGER.error(
        "[Commenter] Failed to post comment on %s#%d: HTTP %s — %s",
        repo, issue_number, response.status_code, response.text[:300],
    )
    return {
        "attempted": True,
        "posted": False,
        "status": f"http_{response.status_code}",
        "comment_url": "",
    }
