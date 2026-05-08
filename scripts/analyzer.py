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
# If effort_hours <= this threshold AND has_poc=False, we force has_poc=True
# because small/medium features should always have a proof-of-concept.
POC_FORCE_EFFORT_THRESHOLD = 80
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
- impact_score: 1-10 based SOLELY on audience size x how central the feature is.
  MANDATORY scale — you MUST use this distribution, not cluster at 6:
    1-2: niche tool, <500 users affected (e.g. obscure CLI flag, edge-case config)
    3-4: useful improvement for a subset of users (~1k-5k devs impacted)
    5-6: notable feature, ~10k-50k devs benefit, non-critical daily workflow
    7-8: high-impact for a large community (100k+ devs), core daily workflow
    9-10: industry-wide, millions of devs, fundamental change to a ubiquitous tool
  EXAMPLES: ripgrep -o flag = 4 (already exists as -o), ripgrep multiline = 6,
    VSCode built-in feature = 8, Python type-hint syntax = 10.
  NEVER give the same score as the previous issue in the same repo.
  If unsure between two scores, pick the LOWER one (be conservative).
- effort_hours: realistic for THIS issue. 8-16h=small CLI flag, 24-40h=focused feature,
  60-80h=parser/protocol change, 100-160h=core engine rewrite, 200h+=architecture overhaul.
  NEVER use 40h or 80h as a default — derive from actual complexity of THIS issue.
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
- CRITICAL: You MUST escape ALL special characters for valid JSON:
  * Newlines: use \\n (two characters: backslash + n), NEVER a literal newline
  * Tabs: use \\t
  * Quotes: use \\"
  * Backslashes: use \\\\
  The entire value must be on ONE line inside the JSON string.

Respond with ONLY the JSON object. No markdown fences. No text outside JSON.\
"""

# CALL 3: RFC only
_SYSTEM_RFC = """\
You are a world-class open-source maintainer. Write a structured RFC proposal.

Return ONLY a JSON object:
{
  "rfc_content": "<full RFC text as a single string>"
}

The RFC must contain all 6 sections (use \\n for newlines inside the string):
1. Summary
2. Motivation
3. Detailed Design
4. Drawbacks
5. Alternatives
6. Unresolved Questions

Minimum 300 words total. Be specific, technical, and actionable.
Respond with ONLY the JSON object. No markdown fences. No text outside JSON.\
"""


# ---------------------------------------------------------------------------
# Utility helpers
# ---------------------------------------------------------------------------

def _preferred_poc_language(repo: str) -> str:
    return REPO_POC_LANGUAGE.get(repo, "python")


def _safe_int(value: Any, min_val: int, max_val: int, default: int) -> int:
    try:
        result = int(value)
        return max(min_val, min(max_val, result))
    except (TypeError, ValueError):
        return default


def _issue_year(issue: dict[str, Any]) -> int:
    try:
        raw = str(issue.get("updated_at", "") or issue.get("created_at", ""))
        return int(raw[:4])
    except (ValueError, IndexError):
        return 2020


def _normalize_tags(tags: Any) -> list[str]:
    if not isinstance(tags, list):
        return []
    normalized: list[str] = []
    for tag in tags:
        tag_str = str(tag).strip().lower()
        if tag_str in _TAGS_LOWER:
            normalized.append(_TAGS_LOWER[tag_str])
        elif tag_str:
            normalized.append(tag_str)
    return normalized[:6]


def _ensure_rfc_sections(text: str) -> str:
    required = ["Summary", "Motivation", "Detailed Design", "Drawbacks",
                "Alternatives", "Unresolved Questions"]
    for section in required:
        if section.lower() not in text.lower():
            text += f"\n\n## {section}\n\nTo be defined."
    return text


def _sanitize_raw_json(raw: str) -> str:
    """
    Fix common LLM JSON output problems before parsing:
    - Replace literal control characters (raw newlines, tabs, etc.) that appear
      INSIDE JSON string values with their escaped equivalents.
    - This handles the model emitting real newlines inside proof_of_concept_code
      instead of the required \\n escape sequences.
    """
    # Strategy: scan char by char tracking whether we are inside a JSON string.
    # When inside a string, replace unescaped control chars with JSON escapes.
    result = []
    in_string = False
    i = 0
    while i < len(raw):
        ch = raw[i]
        if in_string:
            if ch == '\\':
                # Escaped sequence — pass both chars through unchanged
                result.append(ch)
                i += 1
                if i < len(raw):
                    result.append(raw[i])
            elif ch == '"':
                # End of string
                in_string = False
                result.append(ch)
            elif ch == '\n':
                result.append('\\n')
            elif ch == '\r':
                result.append('\\r')
            elif ch == '\t':
                result.append('\\t')
            elif ord(ch) < 0x20:
                # Other control characters — replace with unicode escape
                result.append(f'\\u{ord(ch):04x}')
            else:
                result.append(ch)
        else:
            if ch == '"':
                in_string = True
                result.append(ch)
            else:
                result.append(ch)
        i += 1
    return ''.join(result)


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
    last_error: Exception = ValueError("No attempts made")
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            response = client.chat.completions.create(
                model=MODEL_NAME,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=ANALYZER_TEMPERATURE,
                max_tokens=max_tokens,
            )
            raw_text = response.choices[0].message.content or ""

            # Strip markdown fences if the model added them
            raw_text = re.sub(r"^```(?:json)?\s*", "", raw_text.strip(), flags=re.MULTILINE)
            raw_text = re.sub(r"```\s*$", "", raw_text.strip(), flags=re.MULTILINE)
            raw_text = raw_text.strip()

            # Fix literal control chars inside JSON string values (e.g. raw newlines in PoC code)
            raw_text = _sanitize_raw_json(raw_text)

            parsed = json.loads(raw_text)
            if isinstance(parsed, dict):
                LOGGER.info("[API %s] Attempt %d succeeded.", call_label, attempt)
                return parsed

            raise ValueError(f"Expected dict, got {type(parsed).__name__}")

        except (json.JSONDecodeError, ValueError) as err:
            last_error = err
            LOGGER.warning("[API %s] Attempt %d failed: %s", call_label, attempt, err)
            if attempt < MAX_RETRIES:
                time.sleep(2 ** (attempt - 1))
        except Exception as err:
            last_error = err
            LOGGER.error("[API %s] Attempt %d unexpected error: %s", call_label, attempt, err)
            if attempt < MAX_RETRIES:
                time.sleep(2 ** (attempt - 1))

    raise ValueError(f"All {MAX_RETRIES} attempts failed for {call_label}: {last_error}")


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
        "impact_score: derive from audience size x centrality to daily workflow.\n"
        "effort_hours: be specific to this issue's complexity, not a generic default.\n"
        "Keep prose fields to 3-5 sentences each."
    )


def _coerce_metadata(parsed: dict[str, Any], issue: dict[str, Any]) -> dict[str, Any]:
    parsed["impact_score"] = _safe_int(parsed.get("impact_score"), 1, 10, 5)
    parsed["effort_hours"] = _safe_int(parsed.get("effort_hours"), 1, 10000, 40)
    parsed["death_year"] = _safe_int(parsed.get("death_year"), 2010, 2026, _issue_year(issue))
    parsed["has_poc"] = bool(parsed.get("has_poc", False))
    # Force PoC for small/medium issues (effort <= threshold) regardless of LLM decision.
    effort = parsed.get("effort_hours", 999)
    if not parsed["has_poc"] and isinstance(effort, int) and effort <= POC_FORCE_EFFORT_THRESHOLD:
        LOGGER.info(
            "[Coerce] Forcing has_poc=True (effort=%dh <= threshold=%dh).",
            effort, POC_FORCE_EFFORT_THRESHOLD,
        )
        parsed["has_poc"] = True
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

    # Clean one-liners — ensure complete sentences, no truncation mid-word
    for field in ("one_line_summary", "one_line_why"):
        value = re.sub(r"\s+", " ", str(parsed.get(field, "")).strip())
        value = re.sub(r"\s+(and|or|but|,)\s*$", ".", value, flags=re.IGNORECASE)
        value = re.sub(r"\.{2,}$", ".", value).strip()
        words = value.split()
        if len(words) > ONE_LINE_MAX_WORDS:
            truncated_words = words[:ONE_LINE_MAX_WORDS]
            truncated = " ".join(truncated_words).rstrip(",;:")
            if not truncated.endswith("."):
                truncated += "."
            value = truncated
        if value and value[-1] not in ".!?":
            value += "."
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
        "whose value is the complete runnable code as a single-line JSON string.\n"
        "CRITICAL: escape ALL newlines as \\n, ALL quotes as \\\", ALL backslashes as \\\\\n"
        "The code must be at least 80 lines and include imports and error handling."
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

REQUIRED_METADATA_KEYS = {
    "why_it_died",
    "why_2026_changes_it",
    "modern_design",
    "one_line_summary",
    "one_line_why",
    "effort_hours",
    "impact_score",
    "technology_tags",
    "has_poc",
    "rfc_needed",
    "poc_language",
    "death_year",
    "abandoned_date",
}


def validate_analysis(data: dict[str, Any]) -> tuple[bool, list[str]]:
    errors: list[str] = []

    missing = REQUIRED_METADATA_KEYS - set(data.keys())
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

    # CALL 1 — metadata
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

    # CALL 2 — proof-of-concept code (only if has_poc=True)
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

    # CALL 3 — RFC (only if rfc_needed=True)
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

    # Final validation (best-effort — never blocks the pipeline)
    is_valid, field_errors = validate_analysis(metadata)
    if is_valid:
        LOGGER.info("[Analyzer #%s] Validation passed.", issue_id)
    else:
        for err in field_errors:
            LOGGER.warning("[Analyzer #%s] Validation warning: %s", issue_id, err)
        LOGGER.warning(
            "[Analyzer #%s] Returning best-effort result despite %d warning(s).",
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
            # Mark this repo as recently used so the scanner rotates away from it.
            try:
                from scanner import mark_repo_used
                mark_repo_used(repo)
            except Exception as rot_err:
                LOGGER.warning("[Analyzer] Could not mark repo as used: %s", rot_err)
            return

    LOGGER.warning("[Analyzer] No unresurrected issues found in graveyard.")


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
