from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

from config import RESURRECTION_BASE_FOLDER, STATS_FILE, VOTES_FILE


logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
LOGGER = logging.getLogger(__name__)


def _default_progress() -> dict[str, Any]:
    return {
        "last_updated": "",
        "total_resurrections": 0,
        "total_repos_covered": 0,
        "average_impact_score": 0.0,
        "average_effort_hours": 0.0,
        "top_tags": [],
        "hall_of_fame": [],
        "subscriber_count": 0,
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
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
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
            parsed = json.loads(meta_path.read_text(encoding="utf-8"))
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
