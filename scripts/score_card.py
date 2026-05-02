"""score_card.py

Generates a shareable SVG score card for each resurrection.
"""
from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

LOGGER = logging.getLogger(__name__)
CARD_W = 600
CARD_H = 320
COLOR_BG = "#0d1117"
COLOR_BORDER = "#30363d"
COLOR_PRIMARY = "#3fb950"
COLOR_ACCENT = "#58a6ff"
COLOR_WARNING = "#d29922"
COLOR_TEXT = "#e6edf3"
COLOR_MUTED = "#8b949e"
COLOR_TAG_BG = "#21262d"


def _score_color(score: int) -> str:
    if score >= 8:
        return COLOR_PRIMARY
    if score >= 5:
        return COLOR_WARNING
    return "#f85149"


def _escape_xml(text: str) -> str:
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
        .replace("'", "&apos;")
    )


def _truncate(text: str, max_chars: int) -> str:
    return text if len(text) <= max_chars else text[: max_chars - 1] + "…"


def _progress_bar_svg(x: int, y: int, width: int, height: int, value: int, max_value: int, color: str) -> str:
    filled_w = int((value / max(max_value, 1)) * width)
    return (
        f'<rect x="{x}" y="{y}" width="{width}" height="{height}" rx="{height // 2}" fill="{COLOR_BORDER}"/>'
        f'<rect x="{x}" y="{y}" width="{filled_w}" height="{height}" rx="{height // 2}" fill="{color}"/>'
    )


def _tag_pills(tags: list[str], x_start: int, y: int) -> str:
    svg = ""
    x = x_start
    max_x = CARD_W - 24
    for tag in tags[:6]:
        label = _escape_xml(str(tag))
        tag_w = len(label) * 7 + 20
        if x + tag_w > max_x:
            break
        svg += (
            f'<rect x="{x}" y="{y}" width="{tag_w}" height="20" rx="10" fill="{COLOR_TAG_BG}" stroke="{COLOR_BORDER}" stroke-width="1"/>'
            f'<text x="{x + 10}" y="{y + 14}" font-family="monospace" font-size="11" fill="{COLOR_MUTED}">{label}</text>'
        )
        x += tag_w + 8
    return svg


def generate_score_card(meta: dict[str, Any], output_path: Path) -> None:
    title = _truncate(str(meta.get("title", "Untitled")), 52)
    repo = _escape_xml(str(meta.get("repo", "unknown/unknown")))
    reactions = int(meta.get("reactions", 0))
    impact_score = int(meta.get("impact_score", 0))
    effort_hours = int(meta.get("effort_hours", 0))
    has_poc = bool(meta.get("has_poc", False))
    poc_language = str(meta.get("poc_language", "")).upper() or "N/A"
    date = str(meta.get("date", ""))
    abandoned_date = str(meta.get("abandoned_date", ""))[:10]
    tags = meta.get("technology_tags", []) or []
    one_line_why = _truncate(str(meta.get("one_line_why", "")), 72)
    score_color = _score_color(impact_score)

    poc_badge = (
        f'<rect x="370" y="194" width="90" height="22" rx="11" fill="{COLOR_PRIMARY}" opacity="0.2"/>'
        f'<text x="415" y="209" font-family="monospace" font-size="11" fill="{COLOR_PRIMARY}" text-anchor="middle">PoC { _escape_xml(poc_language) }</text>'
    ) if has_poc else (
        f'<rect x="370" y="194" width="90" height="22" rx="11" fill="{COLOR_BORDER}"/>'
        f'<text x="415" y="209" font-family="monospace" font-size="11" fill="{COLOR_MUTED}" text-anchor="middle">No PoC</text>'
    )

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{CARD_W}" height="{CARD_H}" viewBox="0 0 {CARD_W} {CARD_H}">
  <rect width="{CARD_W}" height="{CARD_H}" rx="12" fill="{COLOR_BG}"/>
  <rect width="{CARD_W}" height="{CARD_H}" rx="12" fill="none" stroke="{COLOR_BORDER}" stroke-width="1.5"/>
  <rect x="0" y="0" width="{CARD_W}" height="3" fill="{COLOR_PRIMARY}"/>
  <rect x="24" y="22" width="120" height="22" rx="11" fill="{COLOR_PRIMARY}" opacity="0.15"/>
  <text x="84" y="37" font-family="monospace" font-size="11" fill="{COLOR_PRIMARY}" text-anchor="middle" font-weight="bold">RESURRECTED</text>
  <text x="{CARD_W - 24}" y="37" font-family="monospace" font-size="11" fill="{COLOR_MUTED}" text-anchor="end">{_escape_xml(date)}</text>
  <text x="24" y="75" font-family="Segoe UI,Arial,sans-serif" font-size="20" font-weight="700" fill="{COLOR_TEXT}">{_escape_xml(title)}</text>
  <text x="24" y="100" font-family="monospace" font-size="13" fill="{COLOR_ACCENT}">{repo}</text>
  <text x="{CARD_W - 24}" y="100" font-family="monospace" font-size="13" fill="{COLOR_MUTED}" text-anchor="end">{reactions:,} 👍</text>
  <line x1="24" y1="116" x2="{CARD_W - 24}" y2="116" stroke="{COLOR_BORDER}" stroke-width="1"/>
  <text x="24" y="140" font-family="Segoe UI,Arial,sans-serif" font-size="13" fill="{COLOR_MUTED}" font-style="italic">{_escape_xml(one_line_why)}</text>
  <text x="24" y="165" font-family="monospace" font-size="12" fill="{COLOR_MUTED}">IMPACT</text>
  <text x="90" y="165" font-family="monospace" font-size="12" fill="{score_color}" font-weight="bold">{impact_score}/10</text>
  {_progress_bar_svg(24, 175, 320, 10, impact_score, 10, score_color)}
  <text x="24" y="212" font-family="monospace" font-size="12" fill="{COLOR_MUTED}">~{effort_hours}h effort</text>
  <text x="160" y="212" font-family="monospace" font-size="12" fill="{COLOR_MUTED}">abandoned { _escape_xml(abandoned_date) }</text>
  {poc_badge}
  {_tag_pills(tags, 24, 230)}
  <line x1="24" y1="268" x2="{CARD_W - 24}" y2="268" stroke="{COLOR_BORDER}" stroke-width="1"/>
  <text x="24" y="288" font-family="monospace" font-size="11" fill="{COLOR_MUTED}">AI Idea Resurrection Lab</text>
  <text x="{CARD_W - 24}" y="288" font-family="monospace" font-size="11" fill="{COLOR_ACCENT}" text-anchor="end">github.com/mohabdelkarim/ai-idea-resurrection-lab</text>
</svg>
"""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(svg, encoding="utf-8")
    LOGGER.info("[ScoreCard] ✅ Score card written to %s", output_path)


def generate_for_resurrection(resurrection_folder: Path, meta: dict[str, Any]) -> Path:
    from config import SCORE_CARD_FILENAME
    output_path = resurrection_folder / SCORE_CARD_FILENAME
    generate_score_card(meta, output_path)
    return output_path
