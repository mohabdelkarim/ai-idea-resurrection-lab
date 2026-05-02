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


# ---------------------------------------------------------------------------
# Static sections (written once into README_TEMPLATE, never overwritten by bot)
# ---------------------------------------------------------------------------

README_TEMPLATE = """<div align="center">

<!-- SECTION:header -->
PLACEHOLDER_HEADER
<!-- END:header -->

<br/>

---

## \U0001f4a1 What Is This?

```
+------------------------------------------------------------------+
|                                                                  |
|  SCAN    GitHub for forgotten, stale and abandoned issues        |
|  FEED    them to an AI model (Groq-powered)                      |
|  GET     technical analysis + PoC code + impact score           |
|  SHIP    results automatically via GitHub Actions               |
|                                                                  |
+------------------------------------------------------------------+
```

Think of it as **a robot archaeologist for open source ideas** -- unearthing
buried potential and turning it into actionable engineering.

<br/>

---

<!-- SECTION:stats -->
PLACEHOLDER_STATS
<!-- END:stats -->

<br/>

---

<!-- SECTION:last -->
PLACEHOLDER_LAST
<!-- END:last -->

<br/>

---

<!-- SECTION:hall-of-fame -->
PLACEHOLDER_HOF
<!-- END:hall-of-fame -->

<br/>

---

## \U0001f6e0\ufe0f Tech Stack

| Layer | Technology |
|-------|------------|
| \U0001f916 AI Engine | [Groq](https://groq.com) -- blazing fast LLM inference |
| \U0001f50e Data Source | GitHub Issues API |
| \U0001f504 Automation | GitHub Actions (daily cron) |
| \U0001f4dd Output | Structured Markdown + code snippets |
| \U0001f40d Language | Python |

<br/>

---

## \U0001f4e8 AI Tool Drop Newsletter

```
+-----------------------------------------------------+
|  AI TOOL DROP -- free weekly newsletter             |
|                                                     |
|  One fresh AI tool, tested honestly                 |
|  One real workflow under 30 minutes                 |
|  One straight verdict -- no fluff                   |
|                                                     |
|  Free. No paywalls. No affiliate links.             |
+-----------------------------------------------------+
```

**[Subscribe Free on Gumroad](https://mohabdelkarim.gumroad.com)**

<br/>

---

<!-- SECTION:community-vote -->
PLACEHOLDER_VOTE
<!-- END:community-vote -->

<br/>

---

## \U0001f468\u200d\U0001f4bb About the Builder

<table align="center">
  <tr>
    <td align="center">
      <b>Mo Abdelkarim</b> -- Software Engineer<br/>
      <sub>Building AI-powered tools that solve real engineering problems.</sub><br/><br/>
      <a href="https://github.com/mohabdelkarim">
        <img src="https://img.shields.io/badge/GitHub-mohabdelkarim-181717?style=flat-square&logo=github" />
      </a>
      &nbsp;
      <a href="https://www.linkedin.com/in/mohamed-abdelkarim-56771b316/">
        <img src="https://img.shields.io/badge/LinkedIn-Connect-0A66C2?style=flat-square&logo=linkedin&logoColor=white" />
      </a>
    </td>
  </tr>
</table>

<br/>

---

<!-- SECTION:footer -->
PLACEHOLDER_FOOTER
<!-- END:footer -->

</div>
"""


# ---------------------------------------------------------------------------
# Section builders
# ---------------------------------------------------------------------------

def build_header_section() -> str:
    body = (
        "<br/>\n\n"
        "> **Every abandoned GitHub issue is a spark that never ignited.**\n"
        "> This lab finds them, analyses them with AI, and ships a proof-of-concept daily.\n\n"
        "<br/>\n\n"
        "![updates daily](https://img.shields.io/badge/updates-daily-00D9A5?style=for-the-badge&logo=github-actions&logoColor=white)\n"
        "![powered by Groq](https://img.shields.io/badge/Powered%20by-Groq-FF6B35?style=for-the-badge&logoColor=white)\n"
        "![license MIT](https://img.shields.io/badge/License-MIT-6C63FF?style=for-the-badge)\n"
        "![built by Mo](https://img.shields.io/badge/Built%20by-Mo%20Abdelkarim-0A66C2?style=for-the-badge&logo=linkedin&logoColor=white)"
    )
    return body


def build_stats_section(progress: dict[str, Any]) -> str:
    total_resurrections = int(progress.get("total_resurrections", 0))
    total_repos_covered = int(progress.get("total_repos_covered", 0))
    average_impact_score = float(progress.get("average_impact_score", 0.0))
    average_effort_hours = float(progress.get("average_effort_hours", 0.0))
    last_updated = _sanitize(progress.get("last_updated", ""))

    body = (
        "## \U0001f4ca Live Stats\n\n"
        "<table align=\"center\">\n"
        "  <tr>\n"
        "    <td align=\"center\"><b>\U0001f9ec Resurrections</b></td>\n"
        "    <td align=\"center\"><b>\U0001f5c2\ufe0f Repos Covered</b></td>\n"
        "    <td align=\"center\"><b>\U0001f4a5 Avg Impact</b></td>\n"
        "    <td align=\"center\"><b>\u23f1\ufe0f Avg Effort</b></td>\n"
        "  </tr>\n"
        "  <tr>\n"
        f"    <td align=\"center\"><code>{total_resurrections}</code></td>\n"
        f"    <td align=\"center\"><code>{total_repos_covered}</code></td>\n"
        f"    <td align=\"center\"><code>{average_impact_score} / 10</code></td>\n"
        f"    <td align=\"center\"><code>~{average_effort_hours}h</code></td>\n"
        "  </tr>\n"
        "</table>\n\n"
        f"<sub>\U0001f550 Last updated: {last_updated}</sub>"
    )
    return body


def build_hall_of_fame_section(progress: dict[str, Any]) -> str:
    hall = progress.get("hall_of_fame", [])
    lines: list[str] = ["## \U0001f3c6 Hall of Fame", ""]
    if not isinstance(hall, list) or not hall:
        lines.append("> *No resurrections yet. Check back tomorrow.*")
        return "\n".join(lines)

    medals = ["\U0001f947", "\U0001f948", "\U0001f949"]
    lines.append("| Rank | Title | Repo | Impact | Why It Matters |")
    lines.append("|:----:|-------|------|:------:|----------------|")
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
            f"| {medal} | [{title}]({original_url}) | `{repo}` | **{impact_score}/10** | {one_line_why} |"
        )

    return "\n".join(lines).strip()


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
                "<table align=\"center\">",
                "  <tr>",
                "    <td>",
                f"      <b><a href=\"{original_url}\">{title}</a></b><br/>",
                f"      <sub>\U0001f4e6 <code>{repo}</code> &nbsp;&#183;&nbsp; "
                f"\U0001f4a5 Impact: <b>{impact_score}/10</b> &nbsp;&#183;&nbsp; "
                f"\U0001f5d3\ufe0f {date}</sub><br/><br/>",
                f"      <i>{one_line_why}</i>",
                "    </td>",
                "  </tr>",
                "</table>",
            ]
        )
    else:
        lines.append("> *The first resurrection is coming soon.*")

    return "\n".join(lines)


def build_vote_section(progress: dict[str, Any]) -> str:
    last = progress.get("last_resurrection")
    lines: list[str] = ["## \U0001f5f3\ufe0f Community Vote", "", "**Should we implement the latest resurrection?**", ""]

    if isinstance(last, dict):
        title = _sanitize(last.get("title", "Untitled"))
        original_url = _sanitize(last.get("original_url", ""))
        lines.append(f"> [{title}]({original_url})")
        lines.append("")

    discussion_url = _sanitize(progress.get("latest_discussion_url", ""))
    if discussion_url:
        lines.append(f"\U0001f449 **[Cast your vote on GitHub Discussions]({discussion_url})**")
    else:
        lines.append("\U0001f449 **[View GitHub Discussions](https://github.com/mohabdelkarim/ai-idea-resurrection-lab/discussions)**")

    return "\n".join(lines)


def build_footer_section(progress: dict[str, Any]) -> str:
    last_updated = _sanitize(progress.get("last_updated", ""))
    return f"<sub>\U0001f9ec Auto-generated by <b>{BOT_NAME}</b> Last run: {last_updated} <a href=\"LICENSE\">MIT License</a></sub>"


# ---------------------------------------------------------------------------
# Section replacement helpers
# ---------------------------------------------------------------------------

def replace_section(content: str, section_name: str, new_body: str) -> str:
    """Replace the content between SECTION markers, preserving the markers."""
    start_marker = f"<!-- SECTION:{section_name} -->"
    end_marker = f"<!-- END:{section_name} -->"
    start = content.find(start_marker)
    end = content.find(end_marker)

    if start == -1 or end == -1 or end < start:
        return content

    before = content[:start + len(start_marker)]
    after = content[end:]
    return f"{before}\n{new_body}\n{after}"


# ---------------------------------------------------------------------------
# Main generator
# ---------------------------------------------------------------------------

def generate_readme(progress: dict[str, Any]) -> str:
    progress = _deep_sanitize(progress)

    # Start from the full creative template
    content = README_TEMPLATE

    # Replace each dynamic section body (markers stay in place)
    content = replace_section(content, "header", build_header_section())
    content = replace_section(content, "stats", build_stats_section(progress))
    content = replace_section(content, "hall-of-fame", build_hall_of_fame_section(progress))
    content = replace_section(content, "last", build_last_section(progress))
    content = replace_section(content, "community-vote", build_vote_section(progress))
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
    safe_content = readme_content.encode("utf-8", errors="ignore").decode("utf-8")
    readme_path.write_text(safe_content, encoding="utf-8")
    LOGGER.info("README.md updated successfully")
