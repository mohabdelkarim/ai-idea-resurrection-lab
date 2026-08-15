"""Unit tests for resurrection lab quality gates."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

from analyzer import (  # noqa: E402
    AnalysisRejected,
    _coerce_metadata,
    _fails_post_analysis_quality,
    _has_generic_filler,
    _is_by_design_rejected,
    _normalize_tags,
    _sanitize_raw_json,
    validate_analysis,
)
from generator import _safe_format, build_meta  # noqa: E402
from issue_commenter import _build_comment, _poc_note  # noqa: E402
from poc_validator import validate_poc_code  # noqa: E402
from scanner import (  # noqa: E402
    _is_closed_as_completed,
    is_abandoned,
)


def test_sanitize_raw_json_escapes_newlines_inside_strings() -> None:
    raw = '{"a": "line1\nline2"}'
    cleaned = _sanitize_raw_json(raw)
    assert json.loads(cleaned)["a"] == "line1\nline2"


def test_by_design_not_planned() -> None:
    assert _is_by_design_rejected({"labels": [], "state_reason": "not_planned"})


def test_by_design_label() -> None:
    assert _is_by_design_rejected({"labels": [{"name": "wontfix"}], "state_reason": None})


def test_normalize_tags_allowlist_only() -> None:
    tags = _normalize_tags(["rust", "MadeUpFramework", "llm"])
    assert "rust" in [t.lower() for t in tags] or any(t.lower() == "rust" for t in tags)
    assert all("madeup" not in t.lower() for t in tags)


def test_generic_filler_detected() -> None:
    text = (
        "Due to ecosystem maturity and growing adoption plus significant progress "
        "in recent years, the landscape has evolved with modern tooling."
    )
    assert _has_generic_filler(text)


def test_impact_gate_no_comment_bypass() -> None:
    issue = {"comments": 50, "reactions": 100}
    analysis = {"impact_score": 2}
    rejected, _ = _fails_post_analysis_quality(issue, analysis)
    assert rejected is True


def test_coerce_disables_poc_for_unsupported_repo() -> None:
    parsed = {
        "impact_score": 7,
        "effort_hours": 30,
        "death_year": 2020,
        "has_poc": True,
        "rfc_needed": False,
        "poc_language": "python",
        "technology_tags": ["rust"],
        "one_line_summary": "This is a complete ten word summary here now.",
        "one_line_why": "Because Rust async traits finally make this feasible today.",
        "why_it_died": "x" * 100,
        "why_2026_changes_it": "y" * 100,
        "modern_design": "z" * 100,
    }
    out = _coerce_metadata(parsed, {"repo": "rails/rails", "updated_at": "2020-01-01T00:00:00Z"})
    assert out["has_poc"] is False


def test_validate_rejects_clustered_effort() -> None:
    data = {
        "why_it_died": "a" * 100,
        "why_2026_changes_it": "Rust 1.75 async traits and tokio make this workable now with PEP 696.",
        "modern_design": "c" * 100,
        "one_line_summary": "Ten words make this summary long enough ok.",
        "one_line_why": "Ten words make this why line long enough ok.",
        "effort_hours": 40,
        "impact_score": 6,
        "technology_tags": ["rust"],
        "has_poc": False,
        "rfc_needed": False,
        "poc_language": "",
        "death_year": 2020,
        "abandoned_date": "2020-01-01",
        "quality_flags": ["clustered_effort_without_justification"],
    }
    ok, errors = validate_analysis(data)
    assert ok is False
    assert any("effort_hours" in e for e in errors)


def test_safe_format_preserves_braces_in_values() -> None:
    out = _safe_format("Body: {body}", body="use {foo} and {bar}")
    assert out == "Body: use {foo} and {bar}"


def test_build_meta_includes_validation_fields() -> None:
    meta = build_meta(
        {"repo": "golang/go", "issue_number": 1, "title": "t", "reactions": 1, "html_url": "u"},
        {
            "abandoned_date": "2020",
            "one_line_why": "why",
            "one_line_summary": "sum",
            "impact_score": 5,
            "effort_hours": 10,
            "has_poc": True,
            "rfc_needed": False,
            "poc_language": "go",
            "poc_validated": True,
            "poc_validation_error": "",
            "quality_flags": [],
            "technology_tags": ["go"],
        },
        "2026-08-15",
        "2026-08-15_golang-go_1",
    )
    assert meta["poc_validated"] is True
    assert "poc_validation_error" in meta


def test_comment_does_not_claim_working_code_without_validation() -> None:
    meta = {
        "impact_score": 5,
        "effort_hours": 10,
        "has_poc": True,
        "poc_validated": False,
        "poc_language": "python",
        "one_line_why": "why it might work now - with better APIs",
        "one_line_summary": "short summary of the idea",
        "date": "2026-08-15",
        "abandoned_date": "2020-01-01",
        "reactions": 10,
        "technology_tags": ["python"],
        "repo": "psf/requests",
        "issue_number": 1,
    }
    note = _poc_note(meta)
    assert "Working" not in note
    assert "notes" in note.lower() or "draft" in note.lower()
    body = _build_comment(meta)
    assert "Working" not in body
    assert "automated pipeline" not in body.lower()
    assert "Resurrection Score" not in body
    assert "AI Idea Resurrection Lab" not in body
    assert "Hey," in body
    assert "analysis" in body.lower()
    # No separator dashes in the comment prose (URLs may still use hyphens in paths)
    prose = "\n".join(
        line for line in body.splitlines()
        if not line.startswith("<!--") and "http" not in line and "](" not in line
    )
    assert " - " not in prose
    assert "—" not in prose
    assert "–" not in prose


def test_poc_validator_python_ok() -> None:
    code = "def main() -> None:\n    print(1)\n\nif __name__ == '__main__':\n    main()\n"
    result = validate_poc_code(code, "python")
    assert result.ok is True


def test_poc_validator_python_syntax_error() -> None:
    result = validate_poc_code("def broken(:\n  pass\n", "python")
    assert result.ok is False


def test_poc_validator_unsupported_language() -> None:
    result = validate_poc_code("puts 'hi'", "ruby")
    assert result.ok is False


def test_state_reason_completed() -> None:
    assert _is_closed_as_completed({"state_reason": "completed"})
    assert not _is_closed_as_completed({"state_reason": "not_planned"})


def test_is_abandoned_skips_prs() -> None:
    issue = {
        "pull_request": {"url": "x"},
        "reactions": {"+1": 100},
        "state": "closed",
        "updated_at": "2020-01-01T00:00:00Z",
        "labels": [{"name": "feature-request"}],
    }
    assert is_abandoned(issue) is False


def test_analysis_rejected_type() -> None:
    with pytest.raises(AnalysisRejected):
        raise AnalysisRejected("bad")
