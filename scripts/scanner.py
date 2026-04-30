from __future__ import annotations

import json
import logging
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from config import GRAVEYARD_FOLDER


logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
LOGGER = logging.getLogger(__name__)


@dataclass(slots=True)
class Issue:
    repo: str
    issue_number: int
    title: str
    body: str
    reactions: int
    created_at: str
    updated_at: str
    labels: list[str]
    url: str
    html_url: str
    author_login: str
    author_profile: str
    already_resurrected: bool = False


@dataclass(slots=True)
class GraveyardEntry:
    repo: str
    issue_number: int
    title: str
    body: str
    reactions: int
    created_at: str
    updated_at: str
    labels: list[str]
    url: str
    html_url: str
    author_login: str
    author_profile: str
    already_resurrected: bool = False


def months_since(date_str: str) -> float:
    parsed = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    delta_days = (datetime.now(timezone.utc) - parsed).total_seconds() / 86400
    return delta_days / 30.4375


def _sanitize_repo_name(repo: str) -> str:
    return repo.replace("/", "__")


def _graveyard_path(repo: str) -> Path:
    return Path(GRAVEYARD_FOLDER) / f"{_sanitize_repo_name(repo)}.json"


def load_graveyard(repo: str) -> list[dict[str, Any]]:
    path = _graveyard_path(repo)
    if not path.exists():
        LOGGER.info("No graveyard file found for %s, starting fresh.", repo)
        return []

    try:
        with path.open("r", encoding="utf-8") as handle:
            data = json.load(handle)
    except json.JSONDecodeError:
        LOGGER.warning("Invalid JSON in %s; resetting graveyard data.", path)
        return []

    if not isinstance(data, list):
        LOGGER.warning("Unexpected data format in %s; expected JSON array.", path)
        return []

    LOGGER.info("Loaded %d existing issues for %s.", len(data), repo)
    return data


def save_graveyard(repo: str, issues: list[dict[str, Any]]) -> None:
    path = _graveyard_path(repo)
    path.parent.mkdir(parents=True, exist_ok=True)
    sorted_issues = sorted(issues, key=lambda item: int(item.get("reactions", 0)), reverse=True)
    serializable = [asdict(GraveyardEntry(**issue)) for issue in sorted_issues]

    with path.open("w", encoding="utf-8") as handle:
        json.dump(serializable, handle, indent=2, ensure_ascii=False)

    LOGGER.info("Saved %d issues to %s.", len(serializable), path)
