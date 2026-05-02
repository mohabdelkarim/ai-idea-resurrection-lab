from __future__ import annotations

import json
import logging
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import Any

from config import RESURRECTION_BASE_FOLDER, STATS_FILE, VOTES_FILE


logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
LOGGER = logging.getLogger(__name__)


def _sanitize(value: Any) -> Any:
    """Recursively strip surrogate characters from all strings in a structure."""
    if isinstance(value, str):
        return value.encode("utf-8", errors="ignore").decode("utf-8", errors="ignore")
    if isinstance(value, dict):
        return {k: _sanitize(v) for k, v in value.items()}
    if isinstance(value, list):
        return [_sanitize(item) for item in value]
    return value


def _default_progress() -> dict[str, Any]:
    return {
        "last_updated": "",
        "total_resurrections": 0,
        "total_repos_covered": 0,
        "average_impact_score": 0.0,
        "average_effort_hours": 0.0,
        "top_tags": [],
        "hall_of_fame": [],
        "last_resurrection": None,
    }


def load_progress() -> dict[str, Any]:
    path = Path(STATS_FILE)
    if not path.exists():
        LOGGER.warning("Progress file not found: %s. Using defaults.", path)
        return _default_progress()

    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as error:
        LOGGER.warning("Invalid progress file %s (%s). Using defaults.", path, error)
        return _default_progress()

    if not isinstance(data, dict):
        LOGGER.warning("Progress file %s is not an object. Using defaults.", path)
        return _default_progress()

    default = _default_progress()
    default.update({key: value for key, value in data.items() if key in default})
    return default


def save_progress(data: dict[str, Any]) -> None:
    path = Path(STATS_FILE)
    path.parent.mkdir(parents=True, exist_ok=True)
    # Sanitize before writing to prevent surrogate characters breaking UTF-8
    safe_data = _sanitize(data)
    path.write_text(json.dumps(safe_data, indent=2, ensure_ascii=True), encoding="utf-8")
    LOGGER.info("Written: %s", path)


def load_all_metas() -> list[dict[str, Any]]:
    base = Path(RESURRECTION_BASE_FOLDER)
    if not base.exists():
        LOGGER.warning("Resurrection base folder not found: %s", base)
        return []

    metas: list[dict[str, Any]] = []
    for child in sorted(base.iterdir()):
        if not child.is_dir():
            continue

        meta_path = child / "meta.json"
        if not meta_path.exists():
            LOGGER.warning("Skipping folder without meta.json: %s", child)
            continue

        try:
            raw = meta_path.read_text(encoding="utf-8")
            parsed = _sanitize(json.loads(raw))
        except (json.JSONDecodeError, OSError) as error:
            LOGGER.warning("Skipping invalid meta.json %s (%s)", meta_path, error)
            continue

        if not isinstance(parsed, dict):
            LOGGER.warning("Skipping malformed meta.json object at %s", meta_path)
            continue

        metas.append(parsed)

    metas.sort(key=lambda item: str(item.get("date", "")))
    LOGGER.info("Loaded %d valid resurrection meta files.", len(metas))
    LOGGER.info("Votes file configured: %s", Path(VOTES_FILE))
    return metas


def compute_top_tags(metas: list[dict[str, Any]], top_n: int = 5) -> list[str]:
    counter: Counter[str] = Counter()
    for meta in metas:
        tags = meta.get("technology_tags", [])
        if not isinstance(tags, list):
            continue
        for tag in tags:
            if isinstance(tag, str) and tag.strip():
                counter[tag] += 1
    return [name for name, _count in counter.most_common(top_n)]


def compute_hall_of_fame(metas: list[dict[str, Any]], top_n: int = 3) -> list[dict[str, Any]]:
    def impact_score(meta: dict[str, Any]) -> int:
        try:
            return int(meta.get("impact_score", 0))
        except (TypeError, ValueError):
            return 0

    top = sorted(metas, key=impact_score, reverse=True)[:top_n]
    return [
        {
            "date": str(meta.get("date", "")),
            "repo": str(meta.get("repo", "")),
            "issue_number": int(meta.get("issue_number", 0)),
            "title": str(meta.get("title", "")),
            "impact_score": impact_score(meta),
            "one_line_why": str(meta.get("one_line_why", "")),
            "original_url": str(meta.get("original_url", "")),
        }
        for meta in top
    ]


def update_stats() -> dict[str, Any]:
    existing_progress = load_progress()
    metas = load_all_metas()

    total_resurrections = len(metas)
    unique_repos = {
        str(meta.get("repo", ""))
        for meta in metas
        if isinstance(meta, dict) and str(meta.get("repo", "")).strip()
    }

    if metas:
        impact_values: list[int] = []
        effort_values: list[int] = []
        for meta in metas:
            try:
                impact_values.append(int(meta.get("impact_score", 0)))
            except (TypeError, ValueError):
                impact_values.append(0)
            try:
                effort_values.append(int(meta.get("effort_hours", 0)))
            except (TypeError, ValueError):
                effort_values.append(0)

        average_impact_score = round(sum(impact_values) / len(impact_values), 2)
        average_effort_hours = round(sum(effort_values) / len(effort_values), 2)
        last_resurrection = max(metas, key=lambda item: str(item.get("date", "")))
    else:
        average_impact_score = 0.0
        average_effort_hours = 0.0
        last_resurrection = None

    new_progress = {
        "last_updated": datetime.now().replace(microsecond=0).isoformat(),
        "total_resurrections": total_resurrections,
        "total_repos_covered": len(unique_repos),
        "average_impact_score": average_impact_score,
        "average_effort_hours": average_effort_hours,
        "top_tags": compute_top_tags(metas, top_n=5),
        "hall_of_fame": compute_hall_of_fame(metas, top_n=3),
        "last_resurrection": last_resurrection,
    }
    save_progress(new_progress)
    return new_progress
