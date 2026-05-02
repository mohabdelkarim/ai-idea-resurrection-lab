from __future__ import annotations

import logging
import sys
from pathlib import Path
from typing import Any

from config import BOT_NAME, STATS_FILE


logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
LOGGER = logging.getLogger(__name__)


def _sanitize(text: Any) -> str:
    """Strip surrogate characters that break UTF-8 encoding."""
    s = str(text) if not isinstance(text, str) else text
    return s.encode("utf-8", errors="ignore").decode("utf-8", errors="ignore")


def _deep_sanitize(value: Any) -> Any:
    """Recursively strip surrogate characters from an entire data structure."""
    if isinstance(value, str):
        return value.encode("utf-8", errors="ignore").decode("utf-8", errors="ignore")
    if isinstance(value, dict):
        return {k: _deep_sanitize(v) for k, v in value.items()}
    if isinstance(value, list):
        return [_deep_sanitize(item) for item in value]
    return value


def _wrap_section(section_name: str, body: str) -> str:
    return f"<!-- SECTION:{section_name} -->\n{body}\n<!-- END:{section_name} -->"


def build_header_section() -> str:
    body = (
        "# \u2699\ufe0f AI Idea Resurrection Lab\n\n"
        "> Abandoned GitHub issues, brought back to life by AI.\n"
        "> Every day: one forgotten idea gets a full technical analysis,\n"
        "> working proof-of-concept code, and an impact score.\n\n"
        "![updates daily](https://img.shields.io/badge/updates-daily-brightgreen?style=for-the-badge)\n"
        "![powered by Groq](https://img.shields.io/badge/powered%20by-Groq-orange?style=for-the-badge)\n"
        "![license MIT](https://img.shields.io/badge/license-MIT-blue?style=for-the-badge)\n"
        "![built by Mo](https://img.shields.io/badge/built%20by-Mo%20Abdelkarim-teal?style=for-the-badge)"
    )
    return _wrap_section("header", body)


def build_stats_section(progress: dict[str, Any]) -> str:
    total_resurrections = int(progress.get("total_resurrections", 0))
    total_repos_covered = int(progress.get("total_repos_covered", 0))
    average_impact_score = float(progress.get("average_impact_score", 0.0))
    average_effort_hours = float(progress.get("average_effort_hours", 0.0))
    last_updated = _sanitize(progress.get("last_updated", ""))

    body = (
        "## \ud83d\udcca Live Stats\n\n"
        "| Metric | Value |\n"
        "|--------|-------|\n"
        f"| \U0001f9ec Total Resurrections | {total_resurrections} |\n"
        f"| \U0001f5c2\ufe0f Repos Covered | {total_repos_covered} |\n"
        f"| \U0001f4a5 Avg Impact Score | {average_impact_score}/10 |\n"
        f"| \u23f1\ufe0f Avg Effort | ~{average_effort_hours}h |\n"
        f"| \U0001f550 Last Updated | {last_updated} |"
    )
    return _wrap_section("stats", body)


def build_hall_of_fame_section(progress: dict[str, Any]) -> str:
    hall = progress.get("hall_of_fame", [])
    lines: list[str] = ["## \U0001f3c6 Hall of Fame", ""]
    if not isinstance(hall, list) or not hall:
        lines.append("> *No resurrections yet. Check back tomorrow.*")
        return _wrap_section("hall-of-fame", "\n".join(lines))

    medals = ["\U0001f947", "\U0001f948", "\U0001f949"]
    lines.append("| Rank | Title | Repo | Impact | Why |")
    lines.append("|------|-------|------|--------|-----|")
    for rank, entry in enumerate(hall[:3], start=1):
        if not isinstance(entry, dict):
            continue
        title = _sanitize(entry.get("title", "Untitled"))
        repo = _sanitize(entry.get("repo", ""))
        impact_score = int(entry.get("impact_score", 0))
        one_line_why = _sanitize(entry.get("one_line_why", ""))
        original_url = _sanitize(entry.get("original_url", ""))
        medal = medals[rank - 1] if rank - 1 < len(medals) else str(rank)
        lines.append(
            f"| {medal} | [{title}]({original_url}) | `{repo}` | {impact_score}/10 | {one_line_why} |"
        )

    return _wrap_section("hall-of-fame", "\n".join(lines).strip())


def build_last_section(progress: dict[str, Any]) -> str:
    last = progress.get("last_resurrection")
    lines: list[str] = ["## \U0001f52c Latest Resurrection", ""]

    if isinstance(last, dict):
        title = _sanitize(last.get("title", "Untitled"))
        original_url = _sanitize(last.get("original_url", ""))
        repo = _sanitize(last.get("repo", ""))
        impact_score = int(last.get("impact_score", 0))
        date = _sanitize(last.get("date", ""))
        one_line_why = _sanitize(last.get("one_line_why", ""))
        lines.extend(
            [
                f"**[{title}]({original_url})**",
                f"\U0001f4e6 `{repo}` \u00b7 \U0001f4a5 Impact: `{impact_score}/10` \u00b7 \U0001f5d3\ufe0f `{date}`",
                f"> {one_line_why}",
            ]
        )
    else:
        lines.append("> *The first resurrection is coming soon.*")

    return _wrap_section("last", "\n".join(lines))


def build_footer_section(progress: dict[str, Any]) -> str:
    last_updated = _sanitize(progress.get("last_updated", ""))
    body = f"---\n*Auto-generated by {BOT_NAME} \u00b7 Last run: {last_updated}*"
    return _wrap_section("footer", body)


def replace_section(content: str, section_name: str, new_section: str) -> str:
    start_marker = f"<!-- SECTION:{section_name} -->"
    end_marker = f"<!-- END:{section_name} -->"
    start = content.find(start_marker)
    end = content.find(end_marker)

    if start != -1 and end != -1 and end >= start:
        end_inclusive = end + len(end_marker)
        before = content[:start].rstrip()
        after = content[end_inclusive:].lstrip()
        if before and after:
            return f"{before}\n\n{new_section}\n\n{after}"
        if before:
            return f"{before}\n\n{new_section}"
        if after:
            return f"{new_section}\n\n{after}"
        return new_section

    if content.strip():
        return f"{content.rstrip()}\n\n{new_section}"
    return new_section


def generate_readme(progress: dict[str, Any]) -> str:
    # FIX: deep-sanitize the entire progress dict before touching any string
    progress = _deep_sanitize(progress)

    content = ""
    content = replace_section(content, "header", build_header_section())
    content = replace_section(content, "stats", build_stats_section(progress))
    content = replace_section(content, "hall-of-fame", build_hall_of_fame_section(progress))
    content = replace_section(content, "last", build_last_section(progress))
    content = replace_section(content, "footer", build_footer_section(progress))
    return content.rstrip() + "\n"


def update_readme() -> None:
    try:
        from scripts.stats import load_progress
    except ImportError:
        script_dir = Path(__file__).parent
        sys.path.insert(0, str(script_dir))
        from stats import load_progress

    progress = load_progress()
    readme_content = generate_readme(progress)

    repo_root = Path(STATS_FILE).parent.parent
    readme_path = repo_root / "README.md"
    # FIX: final encode/decode guard — strip any surviving surrogates before write
    safe_content = readme_content.encode("utf-8", errors="ignore").decode("utf-8")
    readme_path.write_text(safe_content, encoding="utf-8")
    LOGGER.info("README.md updated successfully")
