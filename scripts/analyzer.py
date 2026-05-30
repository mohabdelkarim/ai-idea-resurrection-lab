from __future__ import annotations

import json
import logging
import os
import re
import time
import urllib.request
import uuid
from pathlib import Path
from typing import Any

from groq import Groq

from config import APPROVED_TECHNOLOGY_TAGS


LOGGER = logging.getLogger(__name__)

_TAGS_LOWER = {tag.lower(): tag for tag in APPROVED_TECHNOLOGY_TAGS}

# Maps repo slug → the language its codebase is written in.
REPO_POC_LANGUAGE: dict[str, str] = {
    # Microsoft / TypeScript ecosystem
    "microsoft/vscode": "typescript",
    "microsoft/TypeScript": "typescript",
    "microsoft/semantic-kernel": "python",
    # JavaScript / Node
    "nodejs/node": "typescript",
    "facebook/react": "typescript",
    "vuejs/vue": "typescript",
    "vercel/next.js": "typescript",
    "sveltejs/svelte": "typescript",
    "babel/babel": "typescript",
    "webpack/webpack": "typescript",
    "vitejs/vite": "typescript",
    "prettier/prettier": "typescript",
    "eslint/eslint": "typescript",
    "denoland/deno": "typescript",
    "withastro/astro": "typescript",
    "remix-run/remix": "typescript",
    "open-webui/open-webui": "typescript",
    # Python ecosystem
    "python/cpython": "python",
    "django/django": "python",
    "pallets/flask": "python",
    "psf/requests": "python",
    "huggingface/transformers": "python",
    "pytorch/pytorch": "python",
    "openai/openai-python": "python",
    "langchain-ai/langchain": "python",
    "gradio-app/gradio": "python",
    "streamlit/streamlit": "python",
    "run-llama/llama_index": "python",
    "ggerganov/llama.cpp": "python",
    "comfyanonymous/ComfyUI": "python",
    "ansible/ansible": "python",
    "supabase/supabase": "typescript",
    # Go ecosystem
    "golang/go": "go",
    "hashicorp/terraform": "go",
    "hashicorp/vault": "go",
    "hashicorp/packer": "go",
    "docker/compose": "go",
    "kubernetes/kubernetes": "go",
    "grafana/grafana": "go",
    "prometheus/prometheus": "go",
    "cli/cli": "go",
    "charmbracelet/bubbletea": "go",
    "ollama/ollama": "go",
    # Rust ecosystem
    "rust-lang/rust": "rust",
    "BurntSushi/ripgrep": "rust",
    "sharkdp/bat": "rust",
    "sharkdp/fd": "rust",
    "ajeetdsouza/zoxide": "rust",
    "starship/starship": "rust",
    "alacritty/alacritty": "rust",
    "zellij-org/zellij": "rust",
    "tauri-apps/tauri": "rust",
    "nickel-lang/nickel": "rust",
    # Other
    # Ruby repos → closest supported PoC language is Python
    "rails/rails": "python",
    "ohmyzsh/ohmyzsh": "python",
    "JetBrains/intellij-community": "python",
    "expressjs/express": "typescript",
    "redis/redis": "python",
    "postgres/postgres": "python",
    # C++ repos (llama.cpp, linux, llvm) → Python for PoC since C++ is not in ALLOWED_POC_LANGUAGES
    "torvalds/linux": "python",
    "llvm/llvm-project": "python",
}

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

ALLOWED_POC_LANGUAGES = {"python", "typescript", "rust", "go"}
MIN_ANALYSIS_TEXT_LENGTH = 80
MIN_POC_CODE_LENGTH = 400

# If effort_hours <= this threshold AND has_poc=False, force has_poc=True.
# Small/medium features should always have a proof-of-concept.
POC_FORCE_EFFORT_THRESHOLD = 80

# If impact_score >= this threshold, force has_poc=True regardless of effort.
# High-impact issues (8-10/10) always deserve a PoC even for large features,
# because demonstrating feasibility is most valuable for the biggest ideas.
POC_FORCE_IMPACT_THRESHOLD = 8

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

# Labels that indicate a maintainer consciously rejected the idea.
# Issues carrying any of these must be skipped — they are not resurrection candidates.
_BY_DESIGN_LABELS: frozenset[str] = frozenset({
    "wontfix", "won't fix", "wont fix",
    "by design", "by-design", "bydesign",
    "declined", "not planned", "not-planned",
    "out of scope", "out-of-scope",
    "intentional", "rejected", "invalid",
    "as designed", "as-designed",
})

# ---------------------------------------------------------------------------
# Manifest fetching — grabs real dependencies so the LLM can't hallucinate imports
# ---------------------------------------------------------------------------

# Maps language → candidate manifest filenames (in priority order)
_MANIFEST_CANDIDATES: dict[str, list[str]] = {
    "go":         ["go.mod"],
    "rust":       ["Cargo.toml"],
    "python":     ["requirements.txt", "setup.cfg", "pyproject.toml"],
    "typescript": ["package.json"],
}

# Hard cap: we only send the first N chars of the manifest to the LLM
_MANIFEST_MAX_CHARS = 3000


def _fetch_repo_manifest(repo: str, language: str) -> str:
    """
    Fetch the dependency manifest for *repo* from GitHub's raw content CDN.
    Returns a (possibly truncated) string with the file contents, or an empty
    string if none of the candidate files could be retrieved.

    This is best-effort: network failures are silently swallowed so that the
    rest of the pipeline is never blocked by a missing manifest.
    """
    candidates = _MANIFEST_CANDIDATES.get(language, [])
    for filename in candidates:
        url = f"https://raw.githubusercontent.com/{repo}/HEAD/{filename}"
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "resurrection-bot/1.0"})
            with urllib.request.urlopen(req, timeout=8) as resp:
                if resp.status == 200:
                    content = resp.read().decode("utf-8", errors="replace")
                    if content.strip():
                        LOGGER.info(
                            "[Manifest] Fetched %s for %s (%d chars).",
                            filename, repo, len(content),
                        )
                        return content[:_MANIFEST_MAX_CHARS]
        except Exception as exc:
            LOGGER.debug("[Manifest] Could not fetch %s from %s: %s", filename, repo, exc)
    LOGGER.warning("[Manifest] No manifest found for %s (language=%s).", repo, language)
    return ""


# ---------------------------------------------------------------------------
# Prompts — one focused system prompt per call
# ---------------------------------------------------------------------------

# PRE-CHECK: Is the issue already solved?
_SYSTEM_PRECHECK = """\
You are a senior software engineer with 15+ years of open-source experience.
You have deep knowledge of project histories, major version releases, and
community decisions across the most popular GitHub repositories.

TASK: Determine whether a GitHub issue has ALREADY been fully implemented
or resolved in the CURRENT stable release of the software (as of mid-2026).

═══════════════════════════════════════════════════════
SKILL: Reading Issue Resolution Status
═══════════════════════════════════════════════════════
You will be given:
  - Repository name and issue title
  - Issue description (truncated)
  - Labels applied to the issue
  - state_reason (if available: "completed", "not_planned", "duplicate", or null)

Use ALL of this context together.

═══════════════════════════════════════════════════════
RULES — read every rule before answering
═══════════════════════════════════════════════════════

RULE 1 — ALREADY SOLVED (return true) ONLY IF:
  The feature or fix is fully available in the stable release as of 2026.
  You must be able to name the specific version, flag, or release where
  it landed (e.g. "Implemented in Python 3.13 via PEP 703 --disable-gil flag").
  If you cannot name it precisely, return false.

RULE 2 — REJECTED IS NOT SOLVED (critical):
  If the issue was closed with state_reason="not_planned", or labels include
  ANY of: wontfix, won't fix, by design, by-design, declined, not planned,
  out of scope, intentional, rejected — return already_solved=FALSE.
  A rejected proposal is NEVER solved, even if the feature exists elsewhere.

RULE 3 — PARTIAL SOLUTIONS DO NOT COUNT:
  If the issue is only partially addressed, or requires a workaround,
  return already_solved=false.

RULE 4 — WHEN IN DOUBT, RETURN FALSE:
  False negatives (letting a solved issue through) are caught later.
  False positives (silently dropping a valid resurrection) are unrecoverable.
  Uncertainty = false.

RULE 5 — DO NOT USE GENERAL KNOWLEDGE AS A SUBSTITUTE FOR SPECIFICITY:
  "This is likely implemented by now" is NOT sufficient.
  You must recall a specific version, PR, or changelog entry.

═══════════════════════════════════════════════════════
OUTPUT FORMAT
═══════════════════════════════════════════════════════
Return ONLY a JSON object with exactly these two fields:
{
  "already_solved": <true|false>,
  "reason": "<one sentence — if true: name the version/flag; if false: why not>"
}
No markdown fences. No text outside the JSON object.\
"""

# CALL 1: metadata only (no long-form text, no code)
_SYSTEM_METADATA = """\
You are a world-class senior software architect specialising in open-source
idea resurrection. You analyse abandoned GitHub issues and assess whether
modern tooling makes them viable today.

═══════════════════════════════════════════════════════
SKILL SET
═══════════════════════════════════════════════════════
- Deep knowledge of OSS ecosystem evolution (2015–2026)
- Architecture-level reasoning about implementation cost and feasibility
- Distinguishing "abandoned for good reasons" vs "abandoned due to timing"
- Calibrated scoring: you never cluster scores — you use the full 1–10 scale

═══════════════════════════════════════════════════════
CONTEXT YOU WILL RECEIVE
═══════════════════════════════════════════════════════
The user message contains:
  1. Repository name and issue title
  2. Issue description (original body)
  3. Labels applied to the issue
  4. state_reason (completed / not_planned / duplicate / null)
  5. The preferred poc_language for this repo
  6. A PREVIOUS_SCORE hint (optional) — if present, you MUST use a different score

═══════════════════════════════════════════════════════
RULES — read every rule before generating output
═══════════════════════════════════════════════════════

RULE 1 — REJECT "BY DESIGN" ISSUES BEFORE ANALYSIS:
  If labels include ANY of: wontfix, won't fix, by design, by-design,
  declined, not planned, out of scope, intentional, rejected, invalid —
  OR state_reason = "not_planned" —
  STOP. Do NOT analyse this issue. Return:
  {"__skip__": true, "reason": "<why it is by-design rejected>"}
  This is a hard gate. No exceptions.

RULE 2 — IMPACT SCORE CALIBRATION (mandatory distribution):
  Score based SOLELY on: audience size × centrality to daily workflow.
  You MUST use this scale — never cluster at 6:
    1–2 : niche tool, <500 users affected (obscure CLI flag, edge-case config)
    3–4 : useful for a subset (~1k–5k devs), non-critical path
    5–6 : notable feature, ~10k–50k devs benefit, non-critical daily workflow
    7–8 : high-impact, 100k+ devs, core daily workflow feature
    9–10: industry-wide, millions of devs, fundamental change to ubiquitous tool
  Reference examples:
    ripgrep obscure flag = 3, ripgrep multiline search = 6,
    VSCode core editor feature = 8, Python type-hint syntax change = 10.
  If you received a PREVIOUS_SCORE hint, you MUST pick a different score.
  When torn between two scores, pick the LOWER one (be conservative).

RULE 3 — EFFORT HOURS (derive from THIS issue, never use defaults):
  8–16h   : small CLI flag, config option, one-function change
  24–40h  : focused feature with tests and docs
  60–80h  : parser/protocol change, multi-file refactor
  100–160h: core engine modification, new subsystem
  200h+   : architecture overhaul, cross-cutting concern
  NEVER default to exactly 40h or 80h without specific justification.

RULE 4 — ONE-LINE FIELDS (one_line_summary, one_line_why):
  - Must be a COMPLETE grammatical sentence (subject + verb + object).
  - Exactly 10–20 words. Count the words before writing.
  - Must end with a period.
  - Must NOT end with a conjunction (and, or, but), preposition, article, or comma.
  - one_line_why must explain what SPECIFICALLY changed since the issue was filed —
    name a real technology, API, or ecosystem shift (e.g. "WASM SIMD", "Deno 2.0",
    "Rust async/await stabilisation"). Generic phrases like "user demand" or
    "ecosystem maturity" are NOT acceptable.

RULE 5 — PROSE FIELDS (why_it_died, why_2026_changes_it, modern_design):
  - why_it_died: 3–5 sentences. Name the SPECIFIC technical or social blockers
    that caused abandonment (missing APIs, performance limits, community bandwidth).
  - why_2026_changes_it: 3–5 sentences. Name EXACT tools, crates, packages, or
    language features that now make this feasible. No vague "ecosystem maturity".
  - modern_design: 5–8 sentences. Architecture-level. Name classes, APIs, patterns,
    data structures. This section must be specific enough to guide implementation.

RULE 6 — poc_language:
  Use EXACTLY the language provided in the user message under "Preferred poc_language".
  Do not invent or substitute another language.

RULE 7 — technology_tags:
  Return 3–6 lowercase tags. The first tag must be the name of the repo's primary
  technology (e.g. "vscode", "ripgrep", "deno"). No generic tags like "software"
  or "feature".

═══════════════════════════════════════════════════════
OUTPUT FORMAT
═══════════════════════════════════════════════════════
Return ONLY a JSON object with these exact fields:
{
  "why_it_died": "<3–5 sentences>",
  "why_2026_changes_it": "<3–5 sentences naming exact tools/APIs>",
  "modern_design": "<5–8 sentences, architecture-level>",
  "one_line_summary": "<complete sentence, 10–20 words, ends with period>",
  "one_line_why": "<complete sentence, 10–20 words, names specific tech shift>",
  "impact_score": <integer 1–10>,
  "effort_hours": <positive integer derived from complexity>,
  "technology_tags": ["tag1", "tag2", "tag3"],
  "poc_language": "<python|typescript|rust|go>",
  "death_year": <4-digit integer>,
  "has_poc": <true|false>,
  "rfc_needed": <true|false>,
  "abandoned_date": "<YYYY-MM-DD>"
}
No markdown fences. No text outside the JSON object.\
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

CRITICAL — IMPORTS AND DEPENDENCIES (violations will cause the output to be rejected):
- The user message contains the REAL dependency manifest fetched directly from the
  repository (go.mod / Cargo.toml / package.json / requirements.txt).
- You MUST use ONLY packages that appear in that manifest OR in the language stdlib.
- If the manifest is empty or missing, use ONLY stdlib — no exceptions.
- NEVER invent or guess package names. If you are not 100% certain a package is listed
  in the provided manifest, fall back to stdlib only.
- A stdlib-only PoC is always better than one with a hallucinated dependency.

CRITICAL: You MUST escape ALL special characters for valid JSON:
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
                in_string = False
                result.append(ch)
            elif ch == '\n':
                result.append('\\n')
            elif ch == '\r':
                result.append('\\r')
            elif ch == '\t':
                result.append('\\t')
            elif ord(ch) < 0x20:
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
# By-design label pre-filter — zero API tokens spent on rejected issues
# ---------------------------------------------------------------------------

def _is_by_design_rejected(issue: dict[str, Any]) -> bool:
    """
    Return True if the issue carries any label or state_reason that signals
    a deliberate maintainer decision to not implement it.

    This is a hard gate that runs BEFORE any LLM call, so no tokens are
    wasted on issues that can never be valid resurrection candidates.
    """
    raw_labels = issue.get("labels", [])
    label_names: set[str] = set()
    for lbl in raw_labels:
        if isinstance(lbl, dict):
            label_names.add(str(lbl.get("name", "")).strip().lower())
        else:
            label_names.add(str(lbl).strip().lower())

    if label_names & _BY_DESIGN_LABELS:
        matched = label_names & _BY_DESIGN_LABELS
        LOGGER.info("[ByDesignFilter] Matched labels: %s", matched)
        return True

    state_reason = str(issue.get("state_reason", "") or "").strip().lower()
    if state_reason == "not_planned":
        LOGGER.info("[ByDesignFilter] state_reason=not_planned.")
        return True

    return False


# ---------------------------------------------------------------------------
# Read last impact_score per repo to prevent score repetition
# ---------------------------------------------------------------------------

def _get_last_resurrection_score(repo: str, resurrection_base: str) -> int | None:
    """
    Return the impact_score of the most recent resurrection for this repo,
    or None if there are no previous resurrections for it.
    Used to hint the LLM to avoid repeating the same score.
    """
    base = Path(resurrection_base)
    if not base.exists():
        return None
    candidates: list[tuple[str, int]] = []
    for child in base.iterdir():
        if not child.is_dir():
            continue
        meta_path = child / "meta.json"
        if not meta_path.exists():
            continue
        try:
            meta = json.loads(meta_path.read_text(encoding="utf-8", errors="ignore"))
            if str(meta.get("repo", "")) == repo:
                score = int(meta.get("impact_score", 0))
                candidates.append((child.name, score))
        except (json.JSONDecodeError, OSError, ValueError):
            continue
    if not candidates:
        return None
    candidates.sort(key=lambda x: x[0], reverse=True)
    return candidates[0][1]


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

            # Fix literal control chars inside JSON string values
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
# Pre-check: ask LLM if the issue is already solved before spending tokens
# ---------------------------------------------------------------------------

def _is_already_solved_llm(client: Groq, issue: dict[str, Any]) -> bool:
    """
    Ask the LLM whether this issue is already implemented/solved in the current
    stable version of the software.

    Returns True only when the LLM answers with high confidence (already_solved=true).
    On any error or ambiguous answer, returns False so the issue is NOT skipped.
    This is intentionally conservative: false negatives (letting a solved issue
    through) are caught later by validate_analysis; false positives (dropping a
    valid resurrection) would silently kill a good idea.
    """
    repo = str(issue.get("repo", ""))
    title = str(issue.get("title", ""))
    body = str(issue.get("body") or "")[:1500]  # keep prompt short
    issue_number = issue.get("issue_number", "?")

    # Collect labels as plain strings for the prompt
    raw_labels = issue.get("labels", [])
    label_strings: list[str] = []
    for lbl in raw_labels:
        if isinstance(lbl, dict):
            label_strings.append(str(lbl.get("name", "")).strip())
        else:
            label_strings.append(str(lbl).strip())
    labels_line = ", ".join(label_strings) if label_strings else "none"
    state_reason = str(issue.get("state_reason", "") or "null").strip()

    user_prompt = (
        f"Repository: {repo}\n"
        f"Issue title: {title}\n"
        f"Labels: {labels_line}\n"
        f"state_reason: {state_reason}\n"
        f"Issue description (truncated):\n\"\"\"{body}\"\"\""
    )

    try:
        result = _call_api(
            client,
            _SYSTEM_PRECHECK,
            user_prompt,
            max_tokens=256,
            call_label=f"#{issue_number} precheck",
        )
        already_solved = bool(result.get("already_solved", False))
        reason = str(result.get("reason", "")).strip()
        if already_solved:
            LOGGER.info(
                "[PreCheck] #%s (%s): already solved — %s. Skipping.",
                issue_number, repo, reason,
            )
        else:
            LOGGER.info(
                "[PreCheck] #%s (%s): not solved — %s. Proceeding.",
                issue_number, repo, reason,
            )
        return already_solved
    except Exception as err:
        # On any failure, be conservative: do NOT skip the issue.
        LOGGER.warning(
            "[PreCheck] #%s (%s): pre-check failed (%s) — proceeding with analysis.",
            issue_number, repo, err,
        )
        return False


# ---------------------------------------------------------------------------
# Call 1: metadata
# ---------------------------------------------------------------------------

def _build_metadata_prompt(issue: dict[str, Any], previous_score: int | None = None) -> str:
    repo = str(issue.get("repo", ""))
    preferred_language = _preferred_poc_language(repo)
    previous_score_hint = (
        f"\nPREVIOUS_SCORE hint: the last resurrected issue from {repo} had impact_score={previous_score}."
        f" You MUST pick a DIFFERENT score this time."
        if previous_score is not None
        else ""
    )

    # Collect labels as plain strings for the prompt
    raw_labels = issue.get("labels", [])
    label_strings: list[str] = []
    for lbl in raw_labels:
        if isinstance(lbl, dict):
            label_strings.append(str(lbl.get("name", "")).strip())
        else:
            label_strings.append(str(lbl).strip())
    labels_line = ", ".join(label_strings) if label_strings else "none"
    state_reason = str(issue.get("state_reason", "") or "null").strip()

    return (
        f"ABANDONED GITHUB ISSUE TO RESURRECT:\n"
        f"Repository: {repo}\n"
        f"Title: {issue.get('title', '')}\n"
        f"Originally filed: {issue.get('created_at', '')}\n"
        f"Last activity: {issue.get('updated_at', '')}\n"
        f"Labels: {labels_line}\n"
        f"state_reason: {state_reason}\n\n"
        f"Original description:\n\"\"\"{issue.get('body', '')}\"\"\"\n\n"
        f"Preferred poc_language for this repository: {preferred_language}.\n"
        f"{previous_score_hint}\n"
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

    effort = parsed.get("effort_hours", 999)
    impact = parsed.get("impact_score", 0)

    # Force PoC path 1: small/medium effort (effort <= threshold)
    if not parsed["has_poc"] and isinstance(effort, int) and effort <= POC_FORCE_EFFORT_THRESHOLD:
        LOGGER.info(
            "[Coerce] Forcing has_poc=True (effort=%dh <= effort_threshold=%dh).",
            effort, POC_FORCE_EFFORT_THRESHOLD,
        )
        parsed["has_poc"] = True

    # Force PoC path 2: high-impact issue (impact >= threshold)
    # These are the most valuable resurrections — a PoC is essential to
    # demonstrate feasibility even when implementation is large.
    if not parsed["has_poc"] and isinstance(impact, int) and impact >= POC_FORCE_IMPACT_THRESHOLD:
        LOGGER.info(
            "[Coerce] Forcing has_poc=True (impact_score=%d >= impact_threshold=%d).",
            impact, POC_FORCE_IMPACT_THRESHOLD,
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
            # Try to cut at the last sentence-ending punctuation within the limit
            candidate = " ".join(words[:ONE_LINE_MAX_WORDS])
            last_punct = max(
                candidate.rfind(". "),
                candidate.rfind("! "),
                candidate.rfind("? "),
            )
            if last_punct > len(candidate) // 2:
                value = candidate[: last_punct + 1].strip()
            else:
                truncated = candidate.rstrip(",;:")
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

    # Fetch the real dependency manifest so the LLM can't hallucinate imports
    manifest = _fetch_repo_manifest(repo, language)
    if manifest:
        manifest_section = (
            f"\nREAL DEPENDENCY MANIFEST for {repo} (fetched from GitHub — use ONLY these):\n"
            f"```\n{manifest}\n```\n"
            "Use ONLY packages listed above OR stdlib. Do NOT invent any other package names.\n"
        )
    else:
        manifest_section = (
            f"\nNo dependency manifest could be fetched for {repo}. "
            "Use ONLY the language stdlib — do NOT import any third-party packages.\n"
        )

    return (
        f"ISSUE: {issue.get('title', '')}\n"
        f"Repository: {repo}\n"
        f"Language to use: {language}\n"
        f"{manifest_section}\n"
        f"Architecture summary:\n{metadata.get('modern_design', '')}\n\n"
        f"Original description:\n\"\"\"{issue.get('body', '')}\"\"\"\n\n"
        f"Write the full proof-of-concept in {language}. "
        "Return ONLY a JSON object with a single key 'proof_of_concept_code' "
        "whose value is the complete runnable code as a single-line JSON string.\n"
        "CRITICAL: escape ALL newlines as \\n, ALL quotes as \\\", ALL backslashes as \\\\\n"
        "The code must be at least 80 lines and include imports and error handling.\n"
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
        # Reject sentences ending with dangling conjunctions/prepositions
        dangling = re.search(
            r"\b(and|or|but|the|a|an|in|of|to|for|with|by|from|on|at|into|via)\s*[.!?]?\s*$",
            value, re.IGNORECASE,
        )
        if dangling:
            errors.append(f"{field} ends with dangling word '{dangling.group().strip()}' — incomplete sentence")

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

def analyze_issue(issue: dict[str, Any], previous_score: int | None = None) -> dict[str, Any]:
    from dotenv import load_dotenv
    load_dotenv()

    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        raise EnvironmentError("GROQ_API_KEY not set in .env")
    client = Groq(api_key=api_key)

    issue_id = issue.get("issue_number", "?")

    # CALL 1 — metadata
    LOGGER.info("[Analyzer #%s] Call 1/3: metadata", issue_id)
    metadata_prompt = _build_metadata_prompt(issue, previous_score=previous_score)
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
# Returns the path of the temp file written, so runner can pass it
# explicitly to generator — no shared global state between processes.
# ---------------------------------------------------------------------------

def analyze() -> str:
    """
    Run the full analysis pipeline for one unresurrected issue.

    Returns:
        The absolute path (str) of the temp JSON file written,
        or an empty string if no issue was found to process.
    """
    from config import GRAVEYARD_FOLDER, RESURRECTION_BASE_FOLDER
    from scanner import is_repo_on_cooldown, mark_repo_used, _load_rotation

    api_key = os.environ.get("GROQ_API_KEY", "")
    if not api_key:
        LOGGER.error("[Analyzer] GROQ_API_KEY not set — cannot run pre-check.")
        # Fall through without pre-check rather than crashing the whole pipeline
        client = None
    else:
        from dotenv import load_dotenv
        load_dotenv()
        client = Groq(api_key=api_key)

    rotation = _load_rotation()
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

            if is_repo_on_cooldown(repo, rotation):
                LOGGER.info(
                    "[Analyzer] Skipping #%d (%s) — repo is in rotation cooldown.",
                    issue_number, repo,
                )
                continue

            if (repo, issue_number) in already_resurrected:
                LOGGER.info(
                    "[Analyzer] Skipping #%d (%s) — resurrection folder already exists.",
                    issue_number, repo,
                )
                continue

            # GATE 1 — Label / state_reason pre-filter (zero LLM tokens spent).
            # Issues explicitly rejected by maintainers (wontfix, not_planned, etc.)
            # are not resurrection candidates and must be skipped immediately.
            if _is_by_design_rejected(issue):
                LOGGER.info(
                    "[Analyzer] Skipping #%d (%s) — by-design rejected (labels/state_reason).",
                    issue_number, repo,
                )
                continue

            # GATE 2 — LLM pre-check: is this already solved in the current stable release?
            # Only runs if Groq client is available. On failure returns False (conservative).
            if client is not None and _is_already_solved_llm(client, issue):
                LOGGER.info(
                    "[Analyzer] Skipping #%d (%s) — LLM pre-check: already solved.",
                    issue_number, repo,
                )
                continue

            previous_score = _get_last_resurrection_score(repo, RESURRECTION_BASE_FOLDER)
            if previous_score is not None:
                LOGGER.info(
                    "[Analyzer] Last impact_score for %s was %d — hinting LLM to use a different score.",
                    repo, previous_score,
                )

            LOGGER.info(
                "[Analyzer] Analyzing issue #%s: %s",
                issue.get("issue_number"), issue.get("title"),
            )
            result = analyze_issue(issue, previous_score=previous_score)
            temp_data = {
                "issue": issue,
                "analysis": result["analysis"],
            }

            # Generate a fresh UUID for this specific write — isolated per process/run.
            run_id = uuid.uuid4().hex[:12]
            temp_file = f".analysis_temp_{run_id}.json"
            temp_path = Path(temp_file)
            temp_path.write_text(
                json.dumps(temp_data, indent=2, ensure_ascii=False),
                encoding="utf-8",
            )
            LOGGER.info("[Analyzer] Analysis saved to %s", temp_file)
            mark_repo_used(repo)
            # Return the path so runner.py can pass it explicitly to generator
            return str(temp_path.resolve())

    LOGGER.warning(
        "[Analyzer] No unresurrected issues found in graveyard "
        "(all repos in cooldown or exhausted)."
    )
    return ""


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
