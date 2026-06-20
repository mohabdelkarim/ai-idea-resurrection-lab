from __future__ import annotations

import json
import logging
import os
import re
from datetime import datetime
from pathlib import Path
from typing import Any

from config import BOT_NAME, RESURRECTION_BASE_FOLDER, TEMPLATES_FOLDER


logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
LOGGER = logging.getLogger(__name__)


POC_FILE_MAP = {
    "python": "main.py",
    "typescript": "main.ts",
    "rust": "main.rs",
    "go": "main.go",
}


def _sanitize(value: Any) -> Any:
    """Recursively strip surrogate characters from all strings in a structure."""
    if isinstance(value, str):
        return value.encode("utf-8", errors="ignore").decode("utf-8", errors="ignore")
    if isinstance(value, dict):
        return {k: _sanitize(v) for k, v in value.items()}
    if isinstance(value, list):
        return [_sanitize(item) for item in value]
    return value


def get_poc_extension(language: str) -> str:
    key = str(language).strip().lower()
    return POC_FILE_MAP.get(key, "main.py")


def _slugify(text: str) -> str:
    """Turn an arbitrary string into a safe lowercase slug (max 40 chars)."""
    text = text.lower().strip()
    text = text.replace("/", "-")
    text = re.sub(r"[^a-z0-9-]+", "-", text)
    text = re.sub(r"-{2,}", "-", text)
    return text[:40].strip("-")


def get_issue_folder(base: Path, issue: dict[str, Any]) -> Path:
    """
    Build a unique, human-readable folder name per issue:
      resurrections/<date>_<repo-slug>_<issue-number>

    Example:
      resurrections/2026-05-02_hashicorp-terraform_4084

    This means:
    - Multiple runs on the same day each keep their own folder.
    - The same issue is never written twice (same folder = idempotent update).
    """
    today = datetime.now().strftime("%Y-%m-%d")
    repo_slug = _slugify(str(issue.get("repo", "unknown")))
    issue_number = int(issue.get("issue_number", 0))
    folder_name = f"{today}_{repo_slug}_{issue_number}"
    return base / folder_name


def build_meta(issue: dict[str, Any], analysis: dict[str, Any], today: str, folder_name: str) -> dict[str, Any]:
    meta = {
        "date": today,
        "repo": str(issue.get("repo", "")),
        "issue_number": int(issue.get("issue_number", 0)),
        "title": str(issue.get("title", "")),
        "reactions": int(issue.get("reactions", 0)),
        "abandoned_date": str(analysis.get("abandoned_date", "")),
        "one_line_why": str(analysis.get("one_line_why", "")),
        "impact_score": int(analysis.get("impact_score", 0)),
        "effort_hours": float(analysis.get("effort_hours", 0)),
        "has_poc": bool(analysis.get("has_poc", False)),
        "has_rfc": bool(analysis.get("rfc_needed", False)),
        "poc_language": str(analysis.get("poc_language", "")),
        "technology_tags": list(analysis.get("technology_tags", [])),
        "original_url": str(issue.get("html_url", "")),
        "resurrection_slug": folder_name,
        "comment_posted": False,
        "comment_status": "not_attempted",
        "comment_url": "",
    }
    return _sanitize(meta)


def write_meta_json(folder: Path, meta: dict[str, Any]) -> None:
    path = folder / "meta.json"
    path.write_text(json.dumps(meta, indent=2, ensure_ascii=True), encoding="utf-8")
    LOGGER.info("Written: %s", path)


def _repo_html_url(issue: dict[str, Any]) -> str:
    html_url = str(issue.get("html_url", ""))
    return "/".join(html_url.split("/")[:5]) if html_url else ""


def _labels_text(issue: dict[str, Any]) -> str:
    labels = issue.get("labels", [])
    if not isinstance(labels, list):
        return ""
    return ", ".join(str(label) for label in labels)


def _load_template(name: str) -> str:
    """Read a template file from TEMPLATES_FOLDER. Raises FileNotFoundError if missing."""
    path = Path(TEMPLATES_FOLDER) / name
    return path.read_text(encoding="utf-8")


def write_issue_md(folder: Path, issue: dict[str, Any]) -> None:
    issue = _sanitize(issue)
    content = _load_template("issue_template.md").format(
        title=str(issue.get("title", "")),
        repo=str(issue.get("repo", "")),
        repo_html_url=_repo_html_url(issue),
        issue_number=int(issue.get("issue_number", 0)),
        html_url=str(issue.get("html_url", "")),
        reactions=int(issue.get("reactions", 0)),
        created_at=str(issue.get("created_at", "")),
        updated_at=str(issue.get("updated_at", "")),
        labels=_labels_text(issue),
        body=str(issue.get("body", "")),
        bot_name=BOT_NAME,
    )
    path = folder / "issue.md"
    path.write_text(content, encoding="utf-8")
    LOGGER.info("Written: %s", path)


def write_analysis_md(folder: Path, issue: dict[str, Any], analysis: dict[str, Any]) -> None:
    issue = _sanitize(issue)
    analysis = _sanitize(analysis)
    technology_tags = analysis.get("technology_tags", [])
    tags_text = ", ".join(str(t) for t in technology_tags) if isinstance(technology_tags, list) else ""
    content = _load_template("analysis_template.md").format(
        title=str(issue.get("title", "")),
        one_line_summary=str(analysis.get("one_line_summary", "")),
        one_line_why=str(analysis.get("one_line_why", "")),
        why_it_died=str(analysis.get("why_it_died", "")),
        why_2026_changes_it=str(analysis.get("why_2026_changes_it", "")),
        modern_design=str(analysis.get("modern_design", "")),
        impact_score=int(analysis.get("impact_score", 0)),
        effort_hours=int(analysis.get("effort_hours", 0)),
        tags_text=tags_text,
        death_year=int(analysis.get("death_year", 0)),
        has_poc="Yes" if bool(analysis.get("has_poc", False)) else "No",
        has_rfc="Yes" if bool(analysis.get("rfc_needed", False)) else "No",
        bot_name=BOT_NAME,
    )
    path = folder / "analysis.md"
    path.write_text(content, encoding="utf-8")
    LOGGER.info("Written: %s", path)


def _poc_prerequisites(language: str) -> str:
    key = language.strip().lower()
    prerequisites = {
        "python": "- Python 3.12+, pip install requirements",
        "typescript": "- Node.js 20+, npm install",
        "rust": "- Rust 1.75+, cargo",
        "go": "- Go 1.22+",
    }
    return prerequisites.get(key, prerequisites["python"])


def _poc_run_commands(language: str, file_name: str) -> str:
    key = language.strip().lower()
    commands = {
        "python": f"pip install -r requirements.txt\npython {file_name}",
        "typescript": f"npm install\nnpx ts-node {file_name}",
        "rust": f"rustc {file_name} -o main\n./main",
        "go": f"go run {file_name}",
    }
    return commands.get(key, commands["python"])


def write_poc_files(folder: Path, analysis: dict[str, Any], issue_title: str) -> None:
    if not analysis.get("has_poc"):
        return
    analysis = _sanitize(analysis)
    issue_title = _sanitize(issue_title)
    language = str(analysis.get("poc_language", "python")).strip().lower() or "python"
    poc_code = str(analysis.get("proof_of_concept_code", ""))
    one_line_summary = str(analysis.get("one_line_summary", ""))
    file_name = get_poc_extension(language)

    poc_folder = folder / "poc"
    poc_folder.mkdir(parents=True, exist_ok=True)

    code_path = poc_folder / file_name
    code_path.write_text(poc_code, encoding="utf-8")
    LOGGER.info("Written: %s", code_path)

    readme_content = _load_template("poc_readme_template.md").format(
        issue_title=issue_title,
        language=language,
        prerequisites=_poc_prerequisites(language),
        run_commands=_poc_run_commands(language, file_name),
        one_line_summary=one_line_summary,
    )
    readme_path = poc_folder / "README.md"
    readme_path.write_text(readme_content, encoding="utf-8")
    LOGGER.info("Written: %s", readme_path)


def write_rfc_md(folder: Path, analysis: dict[str, Any], issue_title: str) -> None:
    if not bool(analysis.get("rfc_needed", False)):
        return
    analysis = _sanitize(analysis)
    issue_title = _sanitize(issue_title)
    content = _load_template("rfc_template.md").format(
        issue_title=issue_title,
        rfc_content=str(analysis.get("rfc_content", "")),
        bot_name=BOT_NAME,
    )
    path = folder / "rfc.md"
    path.write_text(content, encoding="utf-8")
    LOGGER.info("Written: %s", path)


def generate_resurrection(issue: dict[str, Any], analysis: dict[str, Any]) -> Path:
    base_folder = Path(RESURRECTION_BASE_FOLDER)
    folder = get_issue_folder(base_folder, issue)
    folder.mkdir(parents=True, exist_ok=True)

    today = datetime.now().strftime("%Y-%m-%d")
    issue_title = _sanitize(str(issue.get("title", "Untitled Issue")))

    write_issue_md(folder, issue)
    write_analysis_md(folder, issue, analysis)
    write_poc_files(folder, analysis, issue_title)
    write_rfc_md(folder, analysis, issue_title)
    meta = build_meta(issue, analysis, today, folder.name)
    write_meta_json(folder, meta)
    LOGGER.info("Resurrection folder ready: %s", folder)
    return folder


def generate(temp_file_path: str = "") -> None:
    """
    Read the analysis temp file and generate all resurrection output files.

    Args:
        temp_file_path: Explicit path to the temp JSON file written by analyze().
                        If empty, falls back to the ANALYSIS_TEMP_PATH env var.
                        This explicit passing eliminates the shared-global race condition
                        that occurred when both analyzer and generator imported a module-level UUID.
    """
    resolved_path = temp_file_path.strip() if temp_file_path else ""
    if not resolved_path:
        resolved_path = os.environ.get("ANALYSIS_TEMP_PATH", "").strip()

    if not resolved_path:
        LOGGER.warning(
            "[Generator] No temp file path provided and ANALYSIS_TEMP_PATH env var not set. "
            "Nothing to generate."
        )
        return

    temp_path = Path(resolved_path)
    if not temp_path.exists():
        LOGGER.error(
            "[Generator] Temp file not found: %s — nothing to generate.", resolved_path
        )
        return

    try:
        data = json.loads(temp_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as e:
        LOGGER.error("[Generator] Cannot read temp file %s: %s", resolved_path, e)
        return

    issue = data.get("issue", {})
    analysis = data.get("analysis", {})

    if not issue or not analysis:
        LOGGER.error("[Generator] Temp file missing 'issue' or 'analysis' keys.")
        return

    folder = generate_resurrection(issue, analysis)

    try:
        temp_path.unlink()
        LOGGER.info("[Generator] Cleaned up temp file: %s", resolved_path)
    except OSError as e:
        LOGGER.warning("[Generator] Could not delete temp file %s: %s", resolved_path, e)

    LOGGER.info("[Generator] Done. Output: %s", folder)
