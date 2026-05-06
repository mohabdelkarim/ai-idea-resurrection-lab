from __future__ import annotations

import json
import logging
import os
import re
import time
from pathlib import Path
from typing import Any

from groq import Groq

from config import APPROVED_TECHNOLOGY_TAGS


LOGGER = logging.getLogger(__name__)

ANALYSIS_TEMP_FILE = ".analysis_temp.json"

_TAGS_LOWER = {tag.lower(): tag for tag in APPROVED_TECHNOLOGY_TAGS}

# Maps repo slug → the language its codebase is written in.
REPO_POC_LANGUAGE: dict[str, str] = {
    "hashicorp/terraform": "go",
    "hashicorp/vault": "go",
    "hashicorp/packer": "go",
    "BurntSushi/ripgrep": "rust",
    "sharkdp/bat": "rust",
    "sharkdp/fd": "rust",
    "ajeetdsouza/zoxide": "rust",
    "starship/starship": "rust",
    "alacritty/alacritty": "rust",
    "zellij-org/zellij": "rust",
    "cli/cli": "go",
    "charmbracelet/bubbletea": "go",
    "ollama/ollama": "go",
    "openai/openai-python": "python",
    "langchain-ai/langchain": "python",
    "gradio-app/gradio": "python",
    "streamlit/streamlit": "python",
    "microsoft/semantic-kernel": "python",
    "run-llama/llama_index": "python",
    "ggerganov/llama.cpp": "python",
    "comfyanonymous/ComfyUI": "python",
    "open-webui/open-webui": "typescript",
}

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

ALLOWED_POC_LANGUAGES = {"python", "typescript", "rust", "go"}
MIN_ANALYSIS_TEXT_LENGTH = 80
MIN_POC_CODE_LENGTH = 400
MIN_RFC_LENGTH = 300
ONE_LINE_MIN_WORDS = 10
ONE_LINE_MAX_WORDS = 20
MODEL_NAME = "meta-llama/llama-4-scout-17b-16e-instruct"
ANALYZER_TEMPERATURE = 0.55
MAX_RETRIES = 4
# Each individual call is small now — 2048 is plenty per call.
MAX_TOKENS_METADATA = 2048
MAX_TOKENS_POC = 4096
MAX_TOKENS_RFC = 3072

# ---------------------------------------------------------------------------
# Prompts — one focused system prompt per call
# ---------------------------------------------------------------------------

# CALL 1: metadata only (no long-form text, no code)
_SYSTEM_METADATA = """\
You are a world-class senior software architect specialising in resurrecting abandoned
open-source ideas.

Given a GitHub issue, return ONLY a JSON object with these fields and NO others:

{
  "why_it_died": "<3-5 specific sentences about why it failed>",
  "why_2026_changes_it": "<3-5 sentences naming exact tools/APIs that exist now>",
  "modern_design": "<5-8 sentences, architecture-level, names classes/APIs/patterns>",
  "one_line_summary": "<single complete sentence 10-20 words>",
  "one_line_why": "<single complete sentence 10-20 words explaining why it succeeds now>",
  "impact_score": <integer 1-10>,
  "effort_hours": <positive integer>,
  "technology_tags": ["tag1", "tag2", "tag3", "tag4"],
  "poc_language": "<python|typescript|rust|go>",
  "death_year": <4-digit integer>,
  "has_poc": <true|false>,
  "rfc_needed": <true|false>,
  "abandoned_date": "<YYYY-MM-DD>"
}

Rules:
- impact_score: 1-10 based SOLELY on audience size × how central the feature is.
  Scale: 1=<100 devs, 5=~20k devs, 8=1M+ devs, 10=industry-wide.
  Use the full range — do NOT cluster around 5 or 7.
- effort_hours: realistic for THIS issue. 8-16h=small, 24-40h=focused, 60-80h=parser/protocol,
  100-160h=core engine, 200h+=architecture overhaul. Never the same for all issues.
- one_line_summary and one_line_why: complete sentences, 10-20 words, NO ellipsis.
- poc_language: use the preferred language from the user message.
- Keep each prose field (why_it_died, why_2026_changes_it, modern_design) to 3-5 sentences.
- Respond with ONLY the JSON object. No markdown fences. No text outside JSON.\
"""

# CALL 2: proof-of-concept code only
_SYSTEM_POC = """\
You are a world-class software engineer. Write a proof-of-concept implementation.

Return ONLY a JSON object:
{
  "proof_of_concept_code": "<full runnable code as a single string>"
}

Requirements for proof_of_concept_code:
- Real, runnable code — NOT pseudocode or a description.
- At least 80 lines. Include imports, error handling, comments.
- Directly demonstrates the core idea from the issue.
- Use the language specified in the user message.
- Escape all special characters properly for JSON (newlines as \\n, quotes as \\", etc.).

Respond with ONLY the JSON object. No markdown fences. No text outside JSON.\
"""

# CALL 3: RFC only
_SYSTEM_RFC = """\
You are a world-class software architect writing an RFC.

Return ONLY a JSON object:
{
  "rfc_content": "<full RFC as a single string>"
}

Requirements for rfc_content:
- Must contain ALL of these sections in order:
  ## Summary
  ## Motivation
  ## Detailed Design
  ## Drawbacks
  ## Alternatives
  ## Unresolved Questions
- Each section must have at least 3 sentences of real technical content.
- The value is a plain string — use \\n for newlines inside the JSON string.

Respond with ONLY the JSON object. No markdown fences. No text outside JSON.\
"""


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _preferred_poc_language(repo: str) -> str:
    return REPO_POC_LANGUAGE.get(repo, "python")


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
    if isinstance(value, bool):
        return default
    try:
        return max(min_val, min(max_val, int(float(str(value)))))
    except (ValueError, TypeError):
        return default


def _ensure_rfc_sections(rfc_text: str) -> str:
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
    if text.startswith("```"):
        lines = text.split("\n")
        inner = lines[1:]
        if inner and inner[-1].strip() == "```":
            inner = inner[:-1]
        text = "\n".join(inner).strip()
    return text


def _extract_json_block(raw: str) -> str:
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


def _load_already_resurrected_keys(resurrection_base: str) -> set[tuple[str, int]]:
    base = Path(resurrection_base)
    resurrected: set[tuple[str, int]] = set()
    if not base.exists():
        return resurrected
    for child in base.iterdir():
        if not child.is_dir():
            continue
        meta_path = child / "meta.json"
        if not meta_path.exists():
            continue
        try:
            meta = json.loads(meta_path.read_text(encoding="utf-8", errors="ignore"))
            repo = str(meta.get("repo", ""))
            issue_number = int(meta.get("issue_number", 0))
            if repo and issue_number:
                resurrected.add((repo, issue_number))
        except (json.JSONDecodeError, OSError, ValueError):
            continue
    return resurrected


# ---------------------------------------------------------------------------
# Low-level: single API call with retries
# ---------------------------------------------------------------------------

def _call_api(
    client: Groq,
    system_prompt: str,
    user_prompt: str,
    max_tokens: int,
    call_label: str,
) -> dict[str, Any]:
    """
    Call the Groq API with retries. Returns the parsed JSON dict.
    Raises ValueError after all retries are exhausted.
    """
    errors: list[str] = []
    last_was_truncated = False

    for attempt in range(1, MAX_RETRIES + 1):
        LOGGER.info("[%s] Attempt %d/%d", call_label, attempt, MAX_RETRIES)

        messages: list[dict[str, str]] = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]

        if attempt > 1 and errors:
            hint = (
                f"Your previous response had issues: {'; '.join(errors[-2:])}. "
                "Fix them and return ONLY the corrected JSON object."
            )
            if last_was_truncated:
                hint += (
                    " IMPORTANT: your last response was truncated. "
                    "Be more concise so the JSON closes properly."
                )
            messages.append({"role": "user", "content": hint})

        try:
            completion = client.chat.completions.create(
                model=MODEL_NAME,
                temperature=ANALYZER_TEMPERATURE,
                max_tokens=max_tokens,
                response_format={"type": "json_object"},
                messages=messages,
            )
            last_was_truncated = False
        except Exception as api_error:
            err_str = str(api_error)
            errors.append(f"Attempt {attempt}: API error — {err_str}")
            LOGGER.error("[%s] API error: %s", call_label, api_error)
            if "json_validate_failed" in err_str or "400" in err_str:
                last_was_truncated = True
            if attempt == MAX_RETRIES:
                raise
            time.sleep(2 ** attempt)
            continue

        raw = _extract_raw_response(completion)
        cleaned = _strip_markdown_fences(raw)
        if not cleaned.startswith("{"):
            cleaned = _extract_json_block(raw)

        try:
            parsed = json.loads(cleaned)
        except json.JSONDecodeError as exc:
            msg = f"Attempt {attempt}: invalid JSON — {exc}"
            errors.append(msg)
            LOGGER.warning("[%s] %s", call_label, msg)
            if attempt == MAX_RETRIES:
                raise ValueError("; ".join(errors)) from exc
            time.sleep(2 ** attempt)
            continue

        if not isinstance(parsed, dict):
            errors.append(f"Attempt {attempt}: response is not a JSON object")
            if attempt == MAX_RETRIES:
                raise ValueError("; ".join(errors))
            time.sleep(2 ** attempt)
            continue

        return parsed

    raise ValueError(f"[{call_label}] failed after {MAX_RETRIES} attempts: {'; '.join(errors)}")


# ---------------------------------------------------------------------------
# Call 1: metadata
# ---------------------------------------------------------------------------

def _build_metadata_prompt(issue: dict[str, Any]) -> str:
    repo = str(issue.get("repo", ""))
    preferred_language = _preferred_poc_language(repo)
    return (
        f"ABANDONED GITHUB ISSUE TO RESURRECT:\n"
        f"Repository: {repo}\n"
        f"Title: {issue.get('title', '')}\n"
        f"Originally filed: {issue.get('created_at', '')}\n"
        f"Last activity: {issue.get('updated_at', '')}\n"
        f"Labels: {', '.join(str(l) for l in issue.get('labels', []))}\n\n"
        f"Original description:\n\"\"\"{issue.get('body', '')}\"\"\"\n\n"
        f"Preferred poc_language for this repository: {preferred_language}.\n"
        "Return ONLY the JSON metadata object as described in your system instructions.\n"
        "impact_score: derive from audience size × centrality to daily workflow.\n"
        "effort_hours: be specific to this issue's complexity, not a generic default.\n"
        "Keep prose fields to 3-5 sentences each."
    )


def _coerce_metadata(parsed: dict[str, Any], issue: dict[str, Any]) -> dict[str, Any]:
    parsed["impact_score"] = _safe_int(parsed.get("impact_score"), 1, 10, 5)
    parsed["effort_hours"] = _safe_int(parsed.get("effort_hours"), 1, 10000, 40)
    parsed["death_year"] = _safe_int(parsed.get("death_year"), 2010, 2026, _issue_year(issue))
    parsed["has_poc"] = bool(parsed.get("has_poc", False))
    parsed["rfc_needed"] = bool(parsed.get("rfc_needed", False))
    parsed["abandoned_date"] = str(issue.get("updated_at", ""))
    parsed["technology_tags"] = _normalize_tags(parsed.get("technology_tags", []))
    if not parsed["technology_tags"]:
        parsed["technology_tags"] = ["open-source"]

    # Enforce the repo's known language
    repo = str(issue.get("repo", ""))
    preferred_lang = _preferred_poc_language(repo)
    if preferred_lang in ALLOWED_POC_LANGUAGES:
        parsed["poc_language"] = preferred_lang
    else:
        lang = str(parsed.get("poc_language", "")).strip().lower()
        parsed["poc_language"] = lang if lang in ALLOWED_POC_LANGUAGES else "python"

    # Clean one-liners
    for field in ("one_line_summary", "one_line_why"):
        value = re.sub(r"\s+", " ", str(parsed.get(field, "")).strip())
        value = re.sub(r"\.{2,}$", ".", value).strip()
        words = value.split()
        if len(words) > ONE_LINE_MAX_WORDS:
            truncated = " ".join(words[:ONE_LINE_MAX_WORDS])
            if not truncated.endswith("."):
                truncated += "."
            value = truncated
        parsed[field] = value

    return parsed


# ---------------------------------------------------------------------------
# Call 2: proof-of-concept code
# ---------------------------------------------------------------------------

def _build_poc_prompt(issue: dict[str, Any], metadata: dict[str, Any]) -> str:
    repo = str(issue.get("repo", ""))
    language = metadata.get("poc_language", _preferred_poc_language(repo))
    return (
        f"ISSUE: {issue.get('title', '')}\n"
        f"Repository: {repo}\n"
        f"Language to use: {language}\n\n"
        f"Architecture summary:\n{metadata.get('modern_design', '')}\n\n"
        f"Original description:\n\"\"\"{issue.get('body', '')}\"\"\"\n\n"
        f"Write the full proof-of-concept in {language}. "
        "Return ONLY a JSON object with a single key 'proof_of_concept_code' "
        "whose value is the complete runnable code as a string.\n"
        "The code must be at least 80 lines, include imports and error handling.\n"
        "Escape all newlines as \\n and quotes as \\\" inside the JSON string."
    )


# ---------------------------------------------------------------------------
# Call 3: RFC
# ---------------------------------------------------------------------------

def _build_rfc_prompt(issue: dict[str, Any], metadata: dict[str, Any]) -> str:
    return (
        f"ISSUE: {issue.get('title', '')}\n"
        f"Repository: {issue.get('repo', '')}\n\n"
        f"One-line summary: {metadata.get('one_line_summary', '')}\n"
        f"Why it died: {metadata.get('why_it_died', '')}\n"
        f"Why 2026 changes it: {metadata.get('why_2026_changes_it', '')}\n"
        f"Modern design: {metadata.get('modern_design', '')}\n\n"
        "Write a complete RFC with all 6 required sections. "
        "Return ONLY a JSON object with a single key 'rfc_content' "
        "whose value is the full RFC text as a string.\n"
        "Use \\n for newlines inside the JSON string value."
    )


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
    errors: list[str] = []

    missing = REQUIRED_KEYS - data.keys()
    if missing:
        errors.append(f"Missing keys: {missing}")
        return False, errors

    impact = data.get("impact_score")
    if not isinstance(impact, int) or not (1 <= impact <= 10):
        errors.append(f"impact_score must be int 1-10, got: {impact!r}")

    effort = data.get("effort_hours")
    if not isinstance(effort, int) or effort <= 0:
        errors.append(f"effort_hours must be positive int, got: {effort!r}")

    for field in ("why_it_died", "why_2026_changes_it", "modern_design"):
        value = str(data.get(field, "")).strip()
        if len(value) < MIN_ANALYSIS_TEXT_LENGTH:
            errors.append(f"{field} too short ({len(value)} chars, min {MIN_ANALYSIS_TEXT_LENGTH})")

    for field in ("one_line_summary", "one_line_why"):
        value = re.sub(r"\s+", " ", str(data.get(field, "")).strip())
        words = value.split()
        if len(words) < ONE_LINE_MIN_WORDS:
            errors.append(f"{field} too short ({len(words)} words, min {ONE_LINE_MIN_WORDS})")
        if len(words) > ONE_LINE_MAX_WORDS:
            errors.append(f"{field} too long ({len(words)} words, max {ONE_LINE_MAX_WORDS})")
        if value.endswith("..."):
            errors.append(f"{field} must not end with ellipsis — write a complete sentence")

    if data.get("has_poc"):
        poc = str(data.get("proof_of_concept_code", "")).strip()
        if len(poc) < MIN_POC_CODE_LENGTH:
            errors.append(f"proof_of_concept_code too short ({len(poc)} chars, min {MIN_POC_CODE_LENGTH})")
        lang = str(data.get("poc_language", "")).strip().lower()
        if lang not in ALLOWED_POC_LANGUAGES:
            errors.append(f"poc_language '{lang}' not in {ALLOWED_POC_LANGUAGES}")

    if data.get("rfc_needed"):
        rfc = str(data.get("rfc_content", "")).strip()
        if len(rfc) < MIN_RFC_LENGTH:
            errors.append(f"rfc_content too short ({len(rfc)} chars, min {MIN_RFC_LENGTH})")

    tags = data.get("technology_tags", [])
    if not isinstance(tags, list) or len(tags) == 0:
        errors.append("technology_tags must be a non-empty list")

    return len(errors) == 0, errors


# ---------------------------------------------------------------------------
# Main entry: 3 sequential focused calls
# ---------------------------------------------------------------------------

def analyze_issue(issue: dict[str, Any]) -> dict[str, Any]:
    from dotenv import load_dotenv
    load_dotenv()

    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        raise EnvironmentError("GROQ_API_KEY not set in .env")
    client = Groq(api_key=api_key)

    issue_id = issue.get("issue_number", "?")

    # ------------------------------------------------------------------
    # CALL 1 — metadata (all scalar fields + short prose)
    # ------------------------------------------------------------------
    LOGGER.info("[Analyzer #%s] Call 1/3: metadata", issue_id)
    metadata_prompt = _build_metadata_prompt(issue)
    metadata_raw = _call_api(
        client, _SYSTEM_METADATA, metadata_prompt, MAX_TOKENS_METADATA, f"#{issue_id} metadata"
    )
    metadata = _coerce_metadata(metadata_raw, issue)
    LOGGER.info(
        "[Analyzer #%s] Metadata done — impact=%d effort=%dh poc=%s rfc=%s lang=%s",
        issue_id,
        metadata["impact_score"],
        metadata["effort_hours"],
        metadata["has_poc"],
        metadata["rfc_needed"],
        metadata["poc_language"],
    )

    # ------------------------------------------------------------------
    # CALL 2 — proof-of-concept code (only if has_poc=True)
    # ------------------------------------------------------------------
    if metadata["has_poc"]:
        LOGGER.info("[Analyzer #%s] Call 2/3: proof-of-concept code", issue_id)
        poc_prompt = _build_poc_prompt(issue, metadata)
        poc_raw = _call_api(
            client, _SYSTEM_POC, poc_prompt, MAX_TOKENS_POC, f"#{issue_id} poc"
        )
        poc_code = str(poc_raw.get("proof_of_concept_code", "")).strip()
        if len(poc_code) < MIN_POC_CODE_LENGTH:
            LOGGER.warning(
                "[Analyzer #%s] PoC code too short (%d chars), marking has_poc=False",
                issue_id, len(poc_code),
            )
            poc_code = ""
            metadata["has_poc"] = False
        metadata["proof_of_concept_code"] = poc_code
        LOGGER.info("[Analyzer #%s] PoC done (%d chars)", issue_id, len(poc_code))
    else:
        metadata["proof_of_concept_code"] = ""
        LOGGER.info("[Analyzer #%s] Skipping PoC (has_poc=False)", issue_id)

    # ------------------------------------------------------------------
    # CALL 3 — RFC (only if rfc_needed=True)
    # ------------------------------------------------------------------
    if metadata["rfc_needed"]:
        LOGGER.info("[Analyzer #%s] Call 3/3: RFC", issue_id)
        rfc_prompt = _build_rfc_prompt(issue, metadata)
        rfc_raw = _call_api(
            client, _SYSTEM_RFC, rfc_prompt, MAX_TOKENS_RFC, f"#{issue_id} rfc"
        )
        rfc_text = str(rfc_raw.get("rfc_content", "")).strip()
        rfc_text = _ensure_rfc_sections(rfc_text)
        if len(rfc_text) < MIN_RFC_LENGTH:
            LOGGER.warning(
                "[Analyzer #%s] RFC too short (%d chars), marking rfc_needed=False",
                issue_id, len(rfc_text),
            )
            rfc_text = ""
            metadata["rfc_needed"] = False
        metadata["rfc_content"] = rfc_text
        LOGGER.info("[Analyzer #%s] RFC done (%d chars)", issue_id, len(rfc_text))
    else:
        metadata["rfc_content"] = ""
        LOGGER.info("[Analyzer #%s] Skipping RFC (rfc_needed=False)", issue_id)

    # ------------------------------------------------------------------
    # Final validation (best-effort — never blocks the pipeline)
    # ------------------------------------------------------------------
    is_valid, field_errors = validate_analysis(metadata)
    if is_valid:
        LOGGER.info("[Analyzer #%s] ✅ Validation passed.", issue_id)
    else:
        for err in field_errors:
            LOGGER.warning("[Analyzer #%s] Validation warning: %s", issue_id, err)
        LOGGER.warning(
            "[Analyzer #%s] ⚠️  Returning best-effort result despite %d warning(s).",
            issue_id, len(field_errors),
        )

    return {"analysis": metadata}


# ---------------------------------------------------------------------------
# Entry point (called by runner.py)
# ---------------------------------------------------------------------------

def analyze() -> None:
    from config import GRAVEYARD_FOLDER, RESURRECTION_BASE_FOLDER

    already_resurrected = _load_already_resurrected_keys(RESURRECTION_BASE_FOLDER)
    LOGGER.info("[Analyzer] %d issues already resurrected (from folders).", len(already_resurrected))

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

            repo = str(issue.get("repo", ""))
            issue_number = int(issue.get("issue_number", 0))
            if (repo, issue_number) in already_resurrected:
                LOGGER.info(
                    "[Analyzer] Skipping #%d (%s) — resurrection folder already exists.",
                    issue_number, repo,
                )
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
            return

    LOGGER.warning("[Analyzer] No unresurrected issues found in graveyard.")
