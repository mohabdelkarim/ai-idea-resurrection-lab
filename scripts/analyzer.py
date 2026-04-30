from __future__ import annotations

from typing import Any

from config import APPROVED_TECHNOLOGY_TAGS


SYSTEM_PROMPT = (
    "You are a senior software architect with 15 years of experience "
    "who specializes in resurrecting abandoned technical ideas from GitHub. "
    "You analyze why ideas failed in their time, what has changed in the "
    "modern ecosystem to make them feasible today, and how to implement "
    "them with current tools. You write precise, honest, technical assessments "
    "— no hype, no fluff. Every analysis must include working proof-of-concept "
    "code that a developer could run today."
)
ALLOWED_POC_LANGUAGES = {"python", "typescript", "rust", "go"}
MAX_ONE_LINE_WORDS = 15


def build_user_prompt(issue: dict[str, Any]) -> str:
    repo = str(issue.get("repo", ""))
    title = str(issue.get("title", ""))
    reactions = int(issue.get("reactions", 0))
    created_at = str(issue.get("created_at", ""))
    updated_at = str(issue.get("updated_at", ""))
    labels = issue.get("labels", [])
    labels_text = ", ".join(str(label) for label in labels) if isinstance(labels, list) else str(labels)
    body = str(issue.get("body", ""))

    return (
        f"Here is an abandoned GitHub issue from {repo}:\n\n"
        f"Title: {title}\n"
        f"Original repository: {repo}\n"
        f"Reactions (upvotes): {reactions}\n"
        f"Created: {created_at}\n"
        f"Last activity: {updated_at}\n"
        f"Labels: {labels_text}\n\n"
        "Original description:\n"
        f"{body}\n\n"
        "Perform a full resurrection analysis. Return ONLY valid JSON matching\n"
        "the required schema. No markdown, no explanation outside the JSON."
    )


def _is_word_limited(text: str, max_words: int) -> bool:
    return len([word for word in text.strip().split() if word]) <= max_words


def validate_analysis(data: dict[str, Any]) -> bool:
    required_keys = {
        "why_it_died",
        "why_2026_changes_it",
        "modern_design",
        "proof_of_concept_code",
        "poc_language",
        "rfc_needed",
        "rfc_content",
        "effort_hours",
        "impact_score",
        "technology_tags",
        "one_line_summary",
        "one_line_why",
        "abandoned_date",
        "has_poc",
        "death_year",
    }
    if not required_keys.issubset(data.keys()):
        return False

    if not isinstance(data["why_it_died"], str):
        return False
    if not isinstance(data["why_2026_changes_it"], str):
        return False
    if not isinstance(data["modern_design"], str):
        return False
    if not isinstance(data["proof_of_concept_code"], str):
        return False
    if not isinstance(data["poc_language"], str):
        return False
    if data["poc_language"] not in ALLOWED_POC_LANGUAGES:
        return False
    if not isinstance(data["rfc_needed"], bool):
        return False
    if data["rfc_content"] is not None and not isinstance(data["rfc_content"], str):
        return False
    if data["rfc_needed"] and not isinstance(data["rfc_content"], str):
        return False
    if not isinstance(data["effort_hours"], int) or data["effort_hours"] <= 0:
        return False
    if not isinstance(data["impact_score"], int) or not (1 <= data["impact_score"] <= 10):
        return False
    if not isinstance(data["technology_tags"], list):
        return False
    if any(not isinstance(tag, str) for tag in data["technology_tags"]):
        return False
    if any(tag not in APPROVED_TECHNOLOGY_TAGS for tag in data["technology_tags"]):
        return False
    if not isinstance(data["one_line_summary"], str) or not _is_word_limited(
        data["one_line_summary"], MAX_ONE_LINE_WORDS
    ):
        return False
    if not isinstance(data["one_line_why"], str) or not _is_word_limited(
        data["one_line_why"], MAX_ONE_LINE_WORDS
    ):
        return False
    if not isinstance(data["abandoned_date"], str):
        return False
    if not isinstance(data["has_poc"], bool):
        return False
    if not isinstance(data["death_year"], int):
        return False
    return True
