from __future__ import annotations

import json
import logging
import os
import re
from pathlib import Path
from typing import Any

from groq import Groq

from config import APPROVED_TECHNOLOGY_TAGS


LOGGER = logging.getLogger(__name__)

ANALYSIS_TEMP_FILE = ".analysis_temp.json"

_TAGS_LOWER = {tag.lower(): tag for tag in APPROVED_TECHNOLOGY_TAGS}

# ---------------------------------------------------------------------------
# Prompts
# ---------------------------------------------------------------------------

SYSTEM_PROMPT = """You are a world-class senior software architect with 20+ years of experience
specializing in resurrecting abandoned open-source ideas. You have deep expertise in
distributed systems, developer tooling, APIs, and modern AI-augmented development.

Your job: take a GitHub issue that was closed or abandoned years ago and produce a
RICH, DETAILED, OPINIONATED technical resurrection analysis.

Guidelines for each field:

- why_it_died: 3-5 sentences. Be SPECIFIC about the technical, ecosystem, or community
  reasons it failed. Name the exact missing pieces (e.g. "The VS Code extension API
  lacked FileDecorationProvider until 2019"). Avoid vague statements like "it was complex".

- why_2026_changes_it: 3-5 sentences. Name SPECIFIC tools, APIs, frameworks, or ecosystem
  shifts that exist today that didn't exist when the issue was filed. Be concrete.
  (e.g. "LLaMA 3.3 running locally, tree-sitter parsers in every editor, Rust-based
  toolchains replacing slow Python build tools").

- modern_design: 5-8 sentences describing a complete technical architecture.
  Name the specific classes, APIs, patterns, and data flows you would use.
  This should read like a senior engineer's architecture note, not a blog post intro.

- proof_of_concept_code: Full, runnable, production-quality code (not pseudocode).
  Must be at least 80 lines. Include imports, error handling, comments.
  The code must directly demonstrate the core idea from the issue.
  Use the language best suited to the original tech stack.

- rfc_content: A structured RFC with these EXACT sections:
  ## Summary\n## Motivation\n## Detailed Design\n## Drawbacks\n## Alternatives\n## Unresolved Questions
  Each section must have at least 3 sentences of real content.

- one_line_summary: One sentence (max 20 words) that captures what the feature does.
- one_line_why: One sentence (max 20 words) explaining WHY it will succeed now.
- impact_score: Integer 1-10. Be honest. If it's niche, give it a 4. Reserve 9-10 for things
  that affect millions of developers. Base it on: audience size, technical novelty, effort ratio.
- effort_hours: Realistic integer. A weekend hack = 8-16h. A production feature = 40-200h.
- technology_tags: 4-6 lowercase tags directly relevant to the implementation stack.
- poc_language: Must be one of: python, typescript, rust, go.
- death_year: The 4-digit year the issue was last active.
- has_poc: true if you wrote real runnable code, false otherwise.
- rfc_needed: true if the feature requires design discussion before implementation.
- abandoned_date: Best estimate of when activity stopped, format YYYY-MM-DD.

CRITICAL RULES:
1. impact_score MUST be an integer between 1 and 10. Never 0. Never null.
2. effort_hours MUST be a positive integer. Never 0. Never null.
3. Every text field must have real, substantive content. No empty strings.
4. proof_of_concept_code must be runnable code, NOT pseudocode or a description.
5. rfc_content MUST contain all 6 sections listed above.
6. Respond with ONLY a valid JSON object. No markdown fences. No explanation outside JSON."""


ALLOWED_POC_LANGUAGES = {"python", "typescript", "rust", "go"}
MIN_ANALYSIS_TEXT_LENGTH = 80   # chars — fields shorter than this are flagged
MIN_POC_CODE_LENGTH = 400       # chars — PoC shorter than this is rejected
MIN_RFC_LENGTH = 300            # chars — RFC shorter than this is rejected
MODEL_NAME = "llama-3.3-70b-versatile"
ANALYZER_TEMPERATURE = 0.35     # lower = more focused, consistent JSON output
MAX_ANALYSIS_RETRIES = 4


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
        f"ABANDONED GITHUB ISSUE TO RESURRECT:\n"
        f"Repository: {repo}\n"
        f"Title: {title}\n"
        f"Community upvotes (reactions): {reactions} 👍 — this idea has STRONG community demand.\n"
        f"Originally filed: {created_at}\n"
        f"Last activity: {updated_at}\n"
        f"Labels: {labels_text}\n\n"
        f"Original description from the issue author:\n"
        f"\"\"\"{body}\"\"\"\n\n"
        "Produce a FULL, DETAILED resurrection analysis following your system instructions.\n"
        "This issue has significant community interest — your analysis should reflect that importance.\n"
        "Return ONLY the JSON object. No markdown. No explanation outside the JSON."
    )


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _normalize_tags(raw_tags: list[Any]) -> list[str]:
    result: list[str] = []
    for raw in raw_tags:
        if not isinstance(raw, str):
            continue
        key = raw.strip().lower()
        if not key:
            continue
        if key in _TAGS_LOWER:
            canonical = _TAGS_LOWER[key]
            if canonical not in result:
                result.append(canonical)
        else:
            if re.match(r'^[a-z0-9][a-z0-9 ./_-]{0,30}$', key) and key not in result:
                result.append(key)
    return result[:6]


def _safe_int(value: Any, min_val: int, max_val: int, default: int) -> int:
    """Parse an integer from AI output, clamping to [min_val, max_val]."""
    if isinstance(value, bool):
        return default
    try:
        parsed = int(float(str(value)))
        return max(min_val, min(max_val, parsed))
    except (ValueError, TypeError):
        return default


def _ensure_rfc_sections(rfc_text: str) -> str:
    """If the RFC is missing required sections, append empty ones so downstream
    renderers always get a complete document."""
    required = [
        "## Summary",
        "## Motivation",
        "## Detailed Design",
        "## Drawbacks",
        "## Alternatives",
        "## Unresolved Questions",
    ]
    result = rfc_text
    for section in required:
        if section.lower() not in result.lower():
            result += f"\n\n{section}\n\n_See analysis.md for full details._"
    return result


def _strip_markdown_fences(raw: str) -> str:
    text = raw.strip()
    # Handle ```json ... ``` or ``` ... ```
    if text.startswith("```"):
        lines = text.split("\n")
        # remove first line (```json or ```) and last line (```)
        inner = lines[1:] if lines[-1].strip() == "```" else lines[1:]
        if inner and inner[-1].strip() == "```":
            inner = inner[:-1]
        text = "\n".join(inner).strip()
    return text


def _extract_json_block(raw: str) -> str:
    """Find the first {...} block in raw text, even if surrounded by prose."""
    start = raw.find("{")
    end = raw.rfind("}")
    if start != -1 and end != -1 and end > start:
        return raw[start:end + 1]
    return raw


def _issue_year(issue: dict[str, Any]) -> int:
    for key in ("updated_at", "created_at"):
        value = str(issue.get(key, ""))
        if value:
            try:
                return int(value[:4])
            except ValueError:
                continue
    return 2020


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


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------

REQUIRED_KEYS = {
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


def validate_analysis(data: dict[str, Any]) -> tuple[bool, list[str]]:
    """Returns (is_valid, list_of_error_messages)."""
    errors: list[str] = []

    # 1. Required keys present
    missing = REQUIRED_KEYS - data.keys()
    if missing:
        errors.append(f"Missing keys: {missing}")
        return False, errors

    # 2. Numeric fields valid
    impact = data.get("impact_score")
    if not isinstance(impact, int) or not (1 <= impact <= 10):
        errors.append(f"impact_score must be int 1-10, got: {impact!r}")

    effort = data.get("effort_hours")
    if not isinstance(effort, int) or effort <= 0:
        errors.append(f"effort_hours must be positive int, got: {effort!r}")

    # 3. Text fields have real content
    for field in ("why_it_died", "why_2026_changes_it", "modern_design",
                  "one_line_summary", "one_line_why"):
        value = str(data.get(field, "")).strip()
        if len(value) < MIN_ANALYSIS_TEXT_LENGTH:
            errors.append(
                f"{field} too short ({len(value)} chars, min {MIN_ANALYSIS_TEXT_LENGTH})"
            )

    # 4. PoC code has real content if has_poc=True
    if data.get("has_poc"):
        poc = str(data.get("proof_of_concept_code", "")).strip()
        if len(poc) < MIN_POC_CODE_LENGTH:
            errors.append(
                f"proof_of_concept_code too short ({len(poc)} chars, min {MIN_POC_CODE_LENGTH})"
            )
        lang = str(data.get("poc_language", "")).strip().lower()
        if lang not in ALLOWED_POC_LANGUAGES:
            errors.append(f"poc_language '{lang}' not in {ALLOWED_POC_LANGUAGES}")

    # 5. RFC has real content if rfc_needed=True
    if data.get("rfc_needed"):
        rfc = str(data.get("rfc_content", "")).strip()
        if len(rfc) < MIN_RFC_LENGTH:
            errors.append(
                f"rfc_content too short ({len(rfc)} chars, min {MIN_RFC_LENGTH})"
            )

    # 6. technology_tags is a non-empty list
    tags = data.get("technology_tags", [])
    if not isinstance(tags, list) or len(tags) == 0:
        errors.append("technology_tags must be a non-empty list")

    return len(errors) == 0, errors


# ---------------------------------------------------------------------------
# Core analysis
# ---------------------------------------------------------------------------

def _coerce_fields(parsed: dict[str, Any], issue: dict[str, Any]) -> dict[str, Any]:
    """Coerce and sanitize all fields after parsing. Never raises."""

    # impact_score: int 1-10, never 0
    parsed["impact_score"] = _safe_int(parsed.get("impact_score"), 1, 10, 5)

    # effort_hours: positive int
    parsed["effort_hours"] = _safe_int(parsed.get("effort_hours"), 1, 10000, 40)

    # death_year
    parsed["death_year"] = _safe_int(
        parsed.get("death_year"), 2010, 2026, _issue_year(issue)
    )

    # booleans
    parsed["has_poc"] = bool(str(parsed.get("proof_of_concept_code", "")).strip())
    parsed["rfc_needed"] = bool(parsed.get("rfc_needed", False))

    # abandoned_date — use issue updated_at as authoritative source
    parsed["abandoned_date"] = str(issue.get("updated_at", ""))

    # technology_tags
    parsed["technology_tags"] = _normalize_tags(parsed.get("technology_tags", []))
    if not parsed["technology_tags"]:
        parsed["technology_tags"] = ["open-source"]

    # poc_language
    lang = str(parsed.get("poc_language", "")).strip().lower()
    parsed["poc_language"] = lang if lang in ALLOWED_POC_LANGUAGES else "python"

    # Ensure RFC has all required sections
    rfc = str(parsed.get("rfc_content", "")).strip()
    parsed["rfc_content"] = _ensure_rfc_sections(rfc) if rfc else ""

    # Truncate one-liners if AI went way over
    for field in ("one_line_summary", "one_line_why"):
        value = str(parsed.get(field, "")).strip()
        if len(value.split()) > 30:
            parsed[field] = " ".join(value.split()[:25]) + "..."

    return parsed


def analyze_issue(issue: dict[str, Any]) -> dict[str, Any]:
    from dotenv import load_dotenv
    load_dotenv()

    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        raise EnvironmentError("GROQ_API_KEY not set in .env")
    client = Groq(api_key=api_key)

    user_prompt = build_user_prompt(issue)
    attempt_errors: list[str] = []

    for attempt in range(1, MAX_ANALYSIS_RETRIES + 1):
        LOGGER.info("[Analyzer] Attempt %d/%d for issue #%s",
                    attempt, MAX_ANALYSIS_RETRIES, issue.get("issue_number"))

        # On later retries, nudge the model with a reminder
        messages: list[dict[str, str]] = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ]
        if attempt > 1 and attempt_errors:
            messages.append({
                "role": "user",
                "content": (
                    f"Your previous response had these issues: {'; '.join(attempt_errors[-3:])}. "
                    "Fix them and return only the corrected JSON object with ALL fields populated "
                    "with substantive content. impact_score must be 1-10. "
                    "proof_of_concept_code must be at least 80 lines of real runnable code."
                ),
            })

        try:
            completion = client.chat.completions.create(
                model=MODEL_NAME,
                temperature=ANALYZER_TEMPERATURE,
                response_format={"type": "json_object"},
                messages=messages,
            )
        except Exception as api_error:
            attempt_errors.append(f"Attempt {attempt}: API error — {api_error}")
            LOGGER.error("[Analyzer] API error: %s", api_error)
            if attempt == MAX_ANALYSIS_RETRIES:
                raise
            continue

        raw_response = _extract_raw_response(completion)
        # Try fence-stripping first, then raw JSON extraction as fallback
        cleaned = _strip_markdown_fences(raw_response)
        if not cleaned.startswith("{"):
            cleaned = _extract_json_block(raw_response)

        try:
            parsed = json.loads(cleaned)
        except json.JSONDecodeError as error:
            msg = f"Attempt {attempt}: invalid JSON — {error}"
            attempt_errors.append(msg)
            LOGGER.warning("[Analyzer] %s", msg)
            if attempt == MAX_ANALYSIS_RETRIES:
                raise ValueError("; ".join(attempt_errors)) from error
            continue

        if not isinstance(parsed, dict):
            attempt_errors.append(f"Attempt {attempt}: response is not a JSON object")
            if attempt == MAX_ANALYSIS_RETRIES:
                raise ValueError("; ".join(attempt_errors))
            continue

        LOGGER.info("[Analyzer] Keys returned: %s", list(parsed.keys()))

        # Coerce all fields (never raises)
        parsed = _coerce_fields(parsed, issue)

        # Validate
        is_valid, field_errors = validate_analysis(parsed)
        if is_valid:
            LOGGER.info(
                "[Analyzer] ✅ Valid analysis. impact=%d effort=%dh poc=%s",
                parsed["impact_score"], parsed["effort_hours"], parsed["has_poc"],
            )
            return {"raw_response": raw_response, "analysis": parsed}

        for err in field_errors:
            LOGGER.warning("[Analyzer] Validation issue: %s", err)
        attempt_errors.extend(field_errors)

        if attempt == MAX_ANALYSIS_RETRIES:
            # Last resort: return the best we have rather than crash the pipeline
            LOGGER.error(
                "[Analyzer] ⚠️ Returning best-effort analysis after %d attempts.",
                MAX_ANALYSIS_RETRIES,
            )
            return {"raw_response": raw_response, "analysis": parsed}

    raise ValueError("Analysis failed after all retries.")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def analyze() -> None:
    from config import GRAVEYARD_FOLDER

    for graveyard_file in sorted(Path(GRAVEYARD_FOLDER).glob("*.json")):
        if graveyard_file.name == ".gitkeep":
            continue
        try:
            with graveyard_file.open(encoding="utf-8") as f:
                issues = json.load(f)
        except (json.JSONDecodeError, OSError) as e:
            LOGGER.error("[Analyzer] Cannot read %s: %s", graveyard_file, e)
            continue

        if not isinstance(issues, list):
            continue

        for issue in issues:
            if not isinstance(issue, dict):
                continue
            if issue.get("already_resurrected"):
                continue

            LOGGER.info(
                "[Analyzer] Analyzing issue #%s: %s",
                issue.get("issue_number"), issue.get("title"),
            )
            result = analyze_issue(issue)
            temp_data = {
                "issue": issue,
                "analysis": result["analysis"],
            }
            Path(ANALYSIS_TEMP_FILE).write_text(
                json.dumps(temp_data, indent=2, ensure_ascii=False),
                encoding="utf-8",
            )
            LOGGER.info("[Analyzer] Analysis saved to %s", ANALYSIS_TEMP_FILE)
            return  # One resurrection per run

    LOGGER.warning("[Analyzer] No unresurrected issues found in graveyard.")
