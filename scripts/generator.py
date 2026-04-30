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
