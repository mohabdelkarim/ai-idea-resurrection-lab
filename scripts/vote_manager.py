from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

from config import STATS_FILE, VOTES_FILE


logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
LOGGER = logging.getLogger(__name__)


def load_votes() -> dict[str, Any]:
    path = Path(VOTES_FILE)
    if not path.exists():
        return {}

    try:
        parsed = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as error:
        LOGGER.warning("Failed to load votes file %s: %s", path, error)
        return {}

    if isinstance(parsed, dict):
        return parsed
    LOGGER.warning("Votes file %s does not contain a JSON object.", path)
    return {}


def save_votes(data: dict[str, Any]) -> None:
    path = Path(VOTES_FILE)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    LOGGER.info("Written: %s", path)


def build_vote_body(meta: dict[str, Any]) -> str:
    title = str(meta.get("title", ""))
    repo = str(meta.get("repo", ""))
    one_line_why = str(meta.get("one_line_why", ""))
    original_url = str(meta.get("original_url", ""))
    impact_score = int(meta.get("impact_score", 0))

    return (
        f"## Community Vote: {title}\n\n"
        f"- **Repository:** `{repo}`\n"
        f"- **Why this matters:** {one_line_why}\n"
        f"- **Original issue:** {original_url}\n"
        f"- **Impact score:** {impact_score}/10\n\n"
        "👍 React with +1 to vote FOR | 👎 React with -1 to vote AGAINST"
    )
