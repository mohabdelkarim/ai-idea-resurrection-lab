from __future__ import annotations

import logging
from typing import Any

from config import BOT_NAME, STATS_FILE


logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
LOGGER = logging.getLogger(__name__)


def _wrap_section(section_name: str, body: str) -> str:
    return f"<!-- SECTION:{section_name} -->\n{body}\n<!-- END:{section_name} -->"


def build_header_section() -> str:
    body = (
        "# 🧬 AI Idea Resurrection Lab\n\n"
        "> Abandoned GitHub issues, brought back to life by AI.\n"
        "> Every day: one forgotten idea gets a full technical analysis,\n"
        "> working proof-of-concept code, and an impact score.\n\n"
        "![updates daily](https://img.shields.io/badge/updates-daily-brightgreen)\n"
        "![powered by GPT-4o](https://img.shields.io/badge/powered%20by-GPT--4o-blue)\n"
        "![license MIT](https://img.shields.io/badge/license-MIT-orange)"
    )
    return _wrap_section("header", body)


def build_stats_section(progress: dict[str, Any]) -> str:
    total_resurrections = int(progress.get("total_resurrections", 0))
    total_repos_covered = int(progress.get("total_repos_covered", 0))
    average_impact_score = float(progress.get("average_impact_score", 0.0))
    average_effort_hours = float(progress.get("average_effort_hours", 0.0))
    subscriber_count = int(progress.get("subscriber_count", 0))
    last_updated = str(progress.get("last_updated", ""))

    body = (
        "## 📊 Live Stats\n\n"
        "| Metric | Value |\n"
        "|--------|-------|\n"
        f"| 🧬 Total Resurrections | {total_resurrections} |\n"
        f"| 🗂️ Repos Covered | {total_repos_covered} |\n"
        f"| 💥 Avg Impact Score | {average_impact_score}/10 |\n"
        f"| ⏱️ Avg Effort | ~{average_effort_hours}h |\n"
        f"| 📬 Subscribers | {subscriber_count} |\n"
        f"| 🕐 Last Updated | {last_updated} |"
    )
    return _wrap_section("stats", body)


def build_hall_of_fame_section(progress: dict[str, Any]) -> str:
    hall = progress.get("hall_of_fame", [])
    lines: list[str] = ["## 🏆 Hall of Fame", ""]
    if not isinstance(hall, list) or not hall:
        lines.append("> *No resurrections yet. Check back tomorrow.*")
        return _wrap_section("hall-of-fame", "\n".join(lines))

    for rank, entry in enumerate(hall[:3], start=1):
        if not isinstance(entry, dict):
            continue
        title = str(entry.get("title", "Untitled"))
        repo = str(entry.get("repo", ""))
        impact_score = int(entry.get("impact_score", 0))
        one_line_why = str(entry.get("one_line_why", ""))
        original_url = str(entry.get("original_url", ""))

        lines.extend(
            [
                f"### {rank}. {title}",
                f"**Repo:** {repo} | **Impact:** {impact_score}/10",
                f"> {one_line_why}",
                f"[View Original Issue]({original_url})",
                "",
            ]
        )

    return _wrap_section("hall-of-fame", "\n".join(lines).strip())
