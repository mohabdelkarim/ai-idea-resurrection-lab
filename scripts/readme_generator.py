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
    s = str(text) if not isinstance(text, str) else text
    return s.encode("utf-8", errors="ignore").decode("utf-8", errors="ignore")


def _deep_sanitize(value: Any) -> Any:
    if isinstance(value, str):
        return value.encode("utf-8", errors="ignore").decode("utf-8", errors="ignore")
    if isinstance(value, dict):
        return {k: _deep_sanitize(v) for k, v in value.items()}
    if isinstance(value, list):
        return [_deep_sanitize(item) for item in value]
    return value


# ---------------------------------------------------------------------------
# The full README template -- static parts never touched by the bot
# ---------------------------------------------------------------------------

README_TEMPLATE = '''\
<div align="center">

<img src="https://capsule-render.vercel.app/api?type=waving&color=0:0f0c29,50:302b63,100:24243e&height=200&section=header&text=AI%20Idea%20Resurrection%20Lab&fontSize=36&fontColor=ffffff&fontAlignY=38&desc=Abandoned%20issues%20brought%20back%20to%20life%20by%20AI&descAlignY=58&descSize=16&animation=fadeIn" />

<!-- SECTION:header -->
{header}
<!-- END:header -->

</div>

---

## \U0001f4a1 What Is This?

```python
def resurrect(issue):
    """
    SCAN   -> find forgotten, stale & abandoned GitHub issues
    FEED   -> run them through Groq-powered AI analysis
    GET    -> technical breakdown + PoC code + impact score
    SHIP   -> auto-publish results daily via GitHub Actions
    """
    return Revival(issue).analyze().score().publish()  # every single day
```

Think of it as **a robot archaeologist for open source** -- unearthing buried potential
and turning forgotten ideas into actionable engineering.

---

<div align="center">

<!-- SECTION:stats -->
{stats}
<!-- END:stats -->

</div>

---

<!-- SECTION:last -->
{last}
<!-- END:last -->

---

<!-- SECTION:hall-of-fame -->
{hof}
<!-- END:hall-of-fame -->

---

## \u2699\ufe0f Tech Stack

<div align="center">

![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![GitHub Actions](https://img.shields.io/badge/GitHub_Actions-2088FF?style=for-the-badge&logo=github-actions&logoColor=white)
![Groq](https://img.shields.io/badge/Groq_AI-FF6B35?style=for-the-badge&logoColor=white)
![Markdown](https://img.shields.io/badge/Markdown-000000?style=for-the-badge&logo=markdown&logoColor=white)

</div>

| Layer | Technology |
|-------|------------|
| \U0001f916 AI Engine | [Groq](https://groq.com) -- blazing fast LLM inference |
| \U0001f50e Data Source | GitHub Issues API |
| \U0001f504 Automation | GitHub Actions (daily cron) |
| \U0001f4dd Output | Structured Markdown + PoC code snippets |
| \U0001f40d Language | Python |

---

## \U0001f4e8 AI Tool Drop Newsletter

<div align="center">

> **Free. Weekly. No fluff.**

| What you get | Details |
|---|---|
| \U0001f6e0\ufe0f One AI tool | Tested honestly, every week |
| \u26a1 One workflow | Under 30 minutes to implement |
| \U0001f3af One verdict | Straight talk, no affiliate links |

**[Subscribe Free](https://mohaabdelkarim.gumroad.com/l/ai-tool-drop)**

</div>

---

<!-- SECTION:community-vote -->
{vote}
<!-- END:community-vote -->

---

## \U0001f468\u200d\U0001f4bb About the Builder

<div align="center">

**Mo Abdelkarim** -- Software Engineer

*Building AI-powered tools that solve real engineering problems.*

[![GitHub](https://img.shields.io/badge/GitHub-mohabdelkarim-181717?style=flat-square&logo=github)](https://github.com/mohabdelkarim)
[![LinkedIn](https://img.shields.io/badge/LinkedIn-Connect-0A66C2?style=flat-square&logo=linkedin&logoColor=white)](https://www.linkedin.com/in/mohamed-abdelkarim-56771b316/)

<br/>

[![Mo\'s GitHub stats](https://github-readme-stats.vercel.app/api?username=mohabdelkarim&show_icons=true&theme=tokyonight&hide_border=true&count_private=true)](https://github.com/mohabdelkarim)

</div>

---

<!-- SECTION:footer -->
{footer}
<!-- END:footer -->

<img src="https://capsule-render.vercel.app/api?type=waving&color=0:24243e,50:302b63,100:0f0c29&height=120&section=footer" />
'''


# ---------------------------------------------------------------------------
# Section builders
# ---------------------------------------------------------------------------

def build_header_section() -> str:
    return (
        "\n> **Every abandoned GitHub issue is a spark that never ignited.**\n"
        "> This lab finds them, analyses them with AI, and ships a proof-of-concept daily.\n\n"
        "<br/>\n\n"
        "[![updates daily](https://img.shields.io/badge/updates-daily-00D9A5?style=for-the-badge&logo=github-actions&logoColor=white)](https://github.com/mohabdelkarim/ai-idea-resurrection-lab/actions)\n"
        "[![powered by Groq](https://img.shields.io/badge/Powered%20by-Groq-FF6B35?style=for-the-badge&logoColor=white)](https://groq.com)\n"
        "[![license MIT](https://img.shields.io/badge/License-MIT-6C63FF?style=for-the-badge)](LICENSE)\n"
        "[![built by Mo](https://img.shields.io/badge/Built%20by-Mo%20Abdelkarim-0A66C2?style=for-the-badge&logo=linkedin&logoColor=white)](https://www.linkedin.com/in/mohamed-abdelkarim-56771b316/)\n"
    )


def build_stats_section(progress: dict[str, Any]) -> str:
    total_resurrections = int(progress.get("total_resurrections", 0))
    total_repos_covered = int(progress.get("total_repos_covered", 0))
    average_impact_score = float(progress.get("average_impact_score", 0.0))
    average_effort_hours = float(progress.get("average_effort_hours", 0.0))
    last_updated = _sanitize(progress.get("last_updated", ""))

    return (
        "## \U0001f4ca Live Stats\n\n"
        "<table>\n"
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
        f"<sub>\U0001f550 Last updated: {last_updated}</sub>\n"
    )


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
        lines += [
            "<table>",
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
    else:
        lines.append("> *The first resurrection is coming soon.*")
    return "\n".join(lines)


def build_vote_section(progress: dict[str, Any]) -> str:
    last = progress.get("last_resurrection")
    lines: list[str] = [
        "## \U0001f5f3\ufe0f Community Vote",
        "",
        "**Should we implement the latest resurrection?**",
        "",
    ]
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
    return (
        "<div align=\"center\">\n"
        f"<sub>\U0001f9ec Auto-generated by <b>{BOT_NAME}</b> "
        f"Last run: {last_updated} "
        "<a href=\"LICENSE\">MIT License</a></sub>\n"
        "</div>\n"
    )


# ---------------------------------------------------------------------------
# Main generator -- builds from template, fills in dynamic sections
# ---------------------------------------------------------------------------

def generate_readme(progress: dict[str, Any]) -> str:
    progress = _deep_sanitize(progress)
    content = README_TEMPLATE.format(
        header=build_header_section(),
        stats=build_stats_section(progress),
        hof=build_hall_of_fame_section(progress),
        last=build_last_section(progress),
        vote=build_vote_section(progress),
        footer=build_footer_section(progress),
    )
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
