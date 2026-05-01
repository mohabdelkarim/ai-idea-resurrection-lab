from __future__ import annotations

import json
import logging
import os
from typing import Any

from groq import Groq

from config import APPROVED_TECHNOLOGY_TAGS


LOGGER = logging.getLogger(__name__)


SYSTEM_PROMPT = (
    "You are a senior software architect with 15 years of experience "
    "who specializes in resurrecting abandoned technical ideas from GitHub. "
    "You analyze why ideas failed in their time, what has changed in the "
    "modern ecosystem to make them feasible today, and how to implement "
    "them with current tools. You write precise, honest, technical assessments "
    "— no hype, no fluff. Every analysis must include working proof-of-concept "
    "code that a developer could run today. "
    "You must respond with a valid JSON object containing EXACTLY these keys: "
    "why_it_died, why_2026_changes_it, modern_design, proof_of_concept_code, "
    "poc_language, rfc_needed, rfc_content, effort_hours, impact_score, "
    "technology_tags, one_line_summary, one_line_why, abandoned_date, "
    "has_poc, death_year. "
    "effort_hours must be an integer, impact_score must be an integer 1-10, "
    "technology_tags must be a list of strings, rfc_needed and has_poc must be booleans. "
    "No markdown, no explanation, only the JSON object."
)
ALLOWED_POC_LANGUAGES = {"python", "typescript", "rust", "go"}
MAX_ONE_LINE_WORDS = 15
MODEL_NAME = "llama-3.3-70b-versatile"
ANALYZER_TEMPERATURE = 0.7
MAX_ANALYSIS_RETRIES = 3
SCHEMA_NAME = "resurrection_analysis"


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
    try:
        effort_hours = int(data["effort_hours"])
        impact_score = int(data["impact_score"])
    except (ValueError, TypeError):
        return False
    if effort_hours <= 0:
        return False
    if not (1 <= impact_score <= 10):
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


def _json_schema() -> dict[str, Any]:
    return {
        "name": SCHEMA_NAME,
        "strict": True,
        "schema": {
            "type": "object",
            "additionalProperties": False,
            "properties": {
                "why_it_died": {"type": "string"},
                "why_2026_changes_it": {"type": "string"},
                "modern_design": {"type": "string"},
                "proof_of_concept_code": {"type": "string"},
                "poc_language": {"type": "string", "enum": sorted(ALLOWED_POC_LANGUAGES)},
                "rfc_needed": {"type": "boolean"},
                "rfc_content": {"type": ["string", "null"]},
                "effort_hours": {"type": "integer"},
                "impact_score": {"type": "integer"},
                "technology_tags": {"type": "array", "items": {"type": "string"}},
                "one_line_summary": {"type": "string"},
                "one_line_why": {"type": "string"},
                "abandoned_date": {"type": "string"},
                "has_poc": {"type": "boolean"},
                "death_year": {"type": "integer"},
            },
            "required": [
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
            ],
        },
    }


def _strip_markdown_fences(raw: str) -> str:
    text = raw.strip()
    if text.startswith("```"):
        text = text.split("```")[1]
        if text.startswith("json"):
            text = text[4:]
    return text.strip()


def _issue_year(issue: dict[str, Any]) -> int:
    candidates = [str(issue.get("created_at", "")), str(issue.get("updated_at", ""))]
    for candidate in candidates:
        if not candidate:
            continue
        try:
            return int(candidate[:4])
        except ValueError:
            continue
    raise ValueError("Issue is missing valid created_at/updated_at year.")


def _extract_raw_response(completion: Any) -> str:
    choice = completion.choices[0]
    content = getattr(choice.message, "content", "")
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        segments: list[str] = []
        for item in content:
            if isinstance(item, dict) and isinstance(item.get("text"), str):
                segments.append(item["text"])
            elif hasattr(item, "text") and isinstance(item.text, str):
                segments.append(item.text)
        return "".join(segments).strip()
    return str(content or "")


def analyze_issue(issue: dict[str, Any]) -> dict[str, Any]:
    from dotenv import load_dotenv

    load_dotenv()
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        raise EnvironmentError("GROQ_API_KEY not set in .env")
    client = Groq(api_key=api_key)

    user_prompt = build_user_prompt(issue)
    errors: list[str] = []

    for attempt in range(1, MAX_ANALYSIS_RETRIES + 1):
        completion = client.chat.completions.create(
            model=MODEL_NAME,
            temperature=ANALYZER_TEMPERATURE,
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
        )
        raw_response = _extract_raw_response(completion)
        cleaned = _strip_markdown_fences(raw_response)

        try:
            parsed = json.loads(cleaned)
            LOGGER.info("GROQ_KEYS: %s", list(parsed.keys()))
        except json.JSONDecodeError as error:
            errors.append(f"Attempt {attempt}: invalid JSON ({error})")
            if attempt == MAX_ANALYSIS_RETRIES:
                raise ValueError("; ".join(errors)) from error
            continue

        if not isinstance(parsed, dict):
            errors.append(f"Attempt {attempt}: parsed payload is not an object.")
            if attempt == MAX_ANALYSIS_RETRIES:
                raise ValueError("; ".join(errors))
            continue

        parsed["abandoned_date"] = str(issue.get("updated_at", ""))
        parsed["has_poc"] = bool(str(parsed.get("proof_of_concept_code", "")).strip())
        parsed["technology_tags"] = [
            tag
            for tag in parsed.get("technology_tags", [])
            if isinstance(tag, str) and tag in APPROVED_TECHNOLOGY_TAGS
        ]

        try:
            parsed["death_year"] = int(parsed.get("death_year"))
        except (TypeError, ValueError):
            parsed["death_year"] = _issue_year(issue)

        if validate_analysis(parsed):
            return {"raw_response": raw_response, "analysis": parsed}

        errors.append(f"Attempt {attempt}: schema validation failed.")
        if attempt == MAX_ANALYSIS_RETRIES:
            raise ValueError("; ".join(errors))

    raise ValueError("Analysis failed after retries.")

def analyze() -> None:
    import json
    from pathlib import Path

    from config import GRAVEYARD_FOLDER

    token = None
    for graveyard_file in Path(GRAVEYARD_FOLDER).glob("*.json"):
        with graveyard_file.open() as f:
            issues = json.load(f)
        for issue in issues:
            if not issue.get("already_resurrected"):
                analyze_issue(issue)
                return  # 1 ανά run
