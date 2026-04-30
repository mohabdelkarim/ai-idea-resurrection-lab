from __future__ import annotations

import json
import logging
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


def get_poc_extension(language: str) -> str:
    key = str(language).strip().lower()
    if key not in POC_FILE_MAP:
        raise ValueError(f"Unsupported PoC language: {language}")
    return POC_FILE_MAP[key]


def get_today_folder(base: Path) -> Path:
    today = datetime.now().strftime("%Y-%m-%d")
    return base / f"day-{today}"


def build_meta(issue: dict[str, Any], analysis: dict[str, Any], today: str) -> dict[str, Any]:
    return {
        "date": today,
        "repo": str(issue.get("repo", "")),
        "issue_number": int(issue.get("issue_number", 0)),
        "title": str(issue.get("title", "")),
        "reactions": int(issue.get("reactions", 0)),
        "abandoned_date": str(analysis.get("abandoned_date", "")),
        "one_line_why": str(analysis.get("one_line_why", "")),
        "impact_score": int(analysis.get("impact_score", 0)),
        "effort_hours": int(analysis.get("effort_hours", 0)),
        "has_poc": bool(analysis.get("has_poc", False)),
        "has_rfc": bool(analysis.get("rfc_needed", False)),
        "poc_language": str(analysis.get("poc_language", "")),
        "technology_tags": list(analysis.get("technology_tags", [])),
        "original_url": str(issue.get("html_url", "")),
    }


def write_meta_json(folder: Path, meta: dict[str, Any]) -> None:
    path = folder / "meta.json"
    path.write_text(json.dumps(meta, indent=2, ensure_ascii=False), encoding="utf-8")
    LOGGER.info("Written: %s", path)


def _repo_html_url(issue: dict[str, Any]) -> str:
    html_url = str(issue.get("html_url", ""))
    return "/".join(html_url.split("/")[:5]) if html_url else ""


def _labels_text(issue: dict[str, Any]) -> str:
    labels = issue.get("labels", [])
    if not isinstance(labels, list):
        return ""
    return ", ".join(str(label) for label in labels)


def write_issue_md(folder: Path, issue: dict[str, Any]) -> None:
    title = str(issue.get("title", ""))
    repo = str(issue.get("repo", ""))
    issue_number = int(issue.get("issue_number", 0))
    html_url = str(issue.get("html_url", ""))
    created_at = str(issue.get("created_at", ""))
    updated_at = str(issue.get("updated_at", ""))
    reactions = int(issue.get("reactions", 0))
    body = str(issue.get("body", ""))
    repo_html_url = _repo_html_url(issue)
    labels = _labels_text(issue)

    content = (
        f"# {title}\n\n"
        f"**Repository:** [{repo}]({repo_html_url})\n"
        f"**Issue:** [{repo}#{issue_number}]({html_url})\n"
        f"**Reactions:** {reactions} 👍\n"
        f"**Created:** {created_at}\n"
        f"**Last Activity:** {updated_at}\n"
        f"**Labels:** {labels}\n\n"
        "---\n\n"
        "## Original Description\n\n"
        f"{body}\n\n"
        "---\n\n"
        f"*Resurrected by {BOT_NAME}*\n"
    )
    path = folder / "issue.md"
    path.write_text(content, encoding="utf-8")
    LOGGER.info("Written: %s", path)


def write_analysis_md(folder: Path, issue: dict[str, Any], analysis: dict[str, Any]) -> None:
    title = str(issue.get("title", ""))
    one_line_summary = str(analysis.get("one_line_summary", ""))
    one_line_why = str(analysis.get("one_line_why", ""))
    why_it_died = str(analysis.get("why_it_died", ""))
    why_2026_changes_it = str(analysis.get("why_2026_changes_it", ""))
    modern_design = str(analysis.get("modern_design", ""))
    impact_score = int(analysis.get("impact_score", 0))
    effort_hours = int(analysis.get("effort_hours", 0))
    technology_tags = analysis.get("technology_tags", [])
    tags_text = ", ".join(str(tag) for tag in technology_tags) if isinstance(technology_tags, list) else ""
    death_year = int(analysis.get("death_year", 0))
    has_poc = "Yes" if bool(analysis.get("has_poc", False)) else "No"
    has_rfc = "Yes" if bool(analysis.get("rfc_needed", False)) else "No"

    content = (
        f"# Analysis: {title}\n\n"
        f"> {one_line_summary}\n\n"
        f"**Why it will work now:** {one_line_why}\n\n"
        "---\n\n"
        "## Why It Died\n\n"
        f"{why_it_died}\n\n"
        "## Why 2026 Changes Everything\n\n"
        f"{why_2026_changes_it}\n\n"
        "## Modern Architecture\n\n"
        f"{modern_design}\n\n"
        "---\n\n"
        "## Resurrection Score\n\n"
        "| Metric | Value |\n"
        "|--------|-------|\n"
        f"| 💥 Impact Score | {impact_score}/10 |\n"
        f"| ⏱️ Effort Estimate | ~{effort_hours} hours |\n"
        f"| 🏷️ Tech Tags | {tags_text} |\n"
        f"| 💀 Year Abandoned | {death_year} |\n"
        f"| 🔬 Has PoC | {has_poc} |\n"
        f"| 📋 Has RFC | {has_rfc} |\n\n"
        "---\n\n"
        f"*Analysis generated by {BOT_NAME}*\n"
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
    if key not in prerequisites:
        raise ValueError(f"Unsupported PoC language: {language}")
    return prerequisites[key]


def _poc_run_commands(language: str, file_name: str) -> str:
    key = language.strip().lower()
    commands = {
        "python": f"pip install -r requirements.txt\npython {file_name}",
        "typescript": f"npm install\nnpx ts-node {file_name}",
        "rust": f"rustc {file_name} -o main\n./main",
        "go": f"go run {file_name}",
    }
    if key not in commands:
        raise ValueError(f"Unsupported PoC language: {language}")
    return commands[key]


def write_poc_files(folder: Path, analysis: dict[str, Any], issue_title: str) -> None:
    language = str(analysis.get("poc_language", "")).strip().lower()
    poc_code = str(analysis.get("proof_of_concept_code", ""))
    one_line_summary = str(analysis.get("one_line_summary", ""))
    file_name = get_poc_extension(language)

    poc_folder = folder / "poc"
    poc_folder.mkdir(parents=True, exist_ok=True)

    code_path = poc_folder / file_name
    code_path.write_text(poc_code, encoding="utf-8")
    LOGGER.info("Written: %s", code_path)

    readme_content = (
        f"# Proof of Concept: {issue_title}\n\n"
        f"**Language:** {language}\n"
        "**Estimated run time:** < 5 minutes\n\n"
        "## Prerequisites\n\n"
        "List the required tools/packages based on poc_language:\n"
        f"{_poc_prerequisites(language)}\n\n"
        "## How to Run\n\n"
        "```bash\n"
        f"{_poc_run_commands(language, file_name)}\n"
        "```\n\n"
        "## What This Demonstrates\n\n"
        f"{one_line_summary}\n"
    )
    readme_path = poc_folder / "README.md"
    readme_path.write_text(readme_content, encoding="utf-8")
    LOGGER.info("Written: %s", readme_path)


def write_rfc_md(folder: Path, analysis: dict[str, Any], issue_title: str) -> None:
    if not bool(analysis.get("rfc_needed", False)):
        return

    rfc_content = str(analysis.get("rfc_content", ""))
    content = (
        f"# RFC: {issue_title}\n\n"
        f"{rfc_content}\n\n"
        "---\n\n"
        f"*RFC generated by {BOT_NAME}*\n"
    )
    path = folder / "rfc.md"
    path.write_text(content, encoding="utf-8")
    LOGGER.info("Written: %s", path)


def generate_resurrection(issue: dict[str, Any], analysis: dict[str, Any]) -> Path:
    base_folder = Path(RESURRECTION_BASE_FOLDER)
    folder = get_today_folder(base_folder)
    folder.mkdir(parents=True, exist_ok=True)

    today = datetime.now().strftime("%Y-%m-%d")
    issue_title = str(issue.get("title", "Untitled Issue"))

    write_issue_md(folder, issue)
    write_analysis_md(folder, issue, analysis)
    write_poc_files(folder, analysis, issue_title)
    write_rfc_md(folder, analysis, issue_title)
    meta = build_meta(issue, analysis, today)
    write_meta_json(folder, meta)

    # Keeps config-driven template root visible in logs for future template migration.
    LOGGER.info("Templates folder configured: %s", Path(TEMPLATES_FOLDER))
    LOGGER.info("Resurrection folder ready: %s", folder)
    return folder
