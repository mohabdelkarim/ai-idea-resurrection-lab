from __future__ import annotations

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import json
import logging
from pathlib import Path
from typing import Any, Callable

from config import RESURRECTION_BASE_FOLDER

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
LOGGER = logging.getLogger(__name__)

REQUIRED_ENV_VARS = (
    "GITHUB_TOKEN",
    "GROQ_API_KEY",
)


def validate_env() -> None:
    missing: list[str] = []
    for var_name in REQUIRED_ENV_VARS:
        if not os.environ.get(var_name, "").strip():
            missing.append(var_name)
    if not missing:
        return
    for var_name in missing:
        LOGGER.error("Missing required environment variable: %s", var_name)
    sys.exit(1)


def export_to_github_env(key: str, value: str) -> None:
    env_file = os.environ.get("GITHUB_ENV", "")
    if not env_file:
        return
    safe_value = value.replace("\r", " ").replace("\n", " ").strip()
    path = Path(env_file)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(f"{key}={safe_value}\n")


def run_step(step_name: str, fn: Callable[[], None]) -> bool:
    LOGGER.info("▶ Running: %s", step_name)
    try:
        fn()
    except Exception as error:
        LOGGER.error("❌ %s failed: %s", step_name, error)
        return False
    LOGGER.info("✅ %s completed.", step_name)
    return True


def load_latest_meta() -> dict[str, Any]:
    base = Path(RESURRECTION_BASE_FOLDER)
    # Folders use format: YYYY-MM-DD_repo_issuenumber (e.g. 2026-05-03_burntsushi-ripgrep_176)
    candidates = sorted(base.glob("*/meta.json"), reverse=True)
    if not candidates:
        LOGGER.warning("No resurrection meta.json files found under %s", base)
        return {}
    latest = candidates[0]
    LOGGER.info("Loading latest meta from: %s", latest)
    try:
        with latest.open("r", encoding="utf-8") as handle:
            parsed = json.load(handle)
        return parsed if isinstance(parsed, dict) else {}
    except Exception as error:
        LOGGER.error("Failed reading latest meta.json %s: %s", latest, error)
        return {}


def export_commit_vars(meta: dict[str, Any]) -> None:
    if not meta:
        LOGGER.error(
            "⚠️  export_commit_vars called with empty meta — "
            "commit message will use fallback values. Check load_latest_meta()."
        )
    export_to_github_env("ISSUE_TITLE", str(meta.get("title", "Unknown")))
    export_to_github_env("ISSUE_REPO", str(meta.get("repo", "unknown/unknown")))
    export_to_github_env("ISSUE_NUMBER", str(meta.get("issue_number", "0")))
    export_to_github_env("ISSUE_URL", str(meta.get("original_url", "")))
    export_to_github_env("IMPACT_SCORE", str(meta.get("impact_score", 0)))
    export_to_github_env("EFFORT_HOURS", str(meta.get("effort_hours", 0)))
    export_to_github_env("HAS_POC", "true" if meta.get("has_poc") else "false")
    export_to_github_env("ABANDONED_DATE", str(meta.get("abandoned_date", "unknown")))
    export_to_github_env("ONE_LINE_WHY", str(meta.get("one_line_why", "")))


def run_pipeline() -> None:
    results: list[bool] = []

    def _scanner_step() -> None:
        from scanner import scan_issues
        scan_issues()

    def _analyzer_step() -> None:
        from analyzer import analyze
        analyze()

    def _generator_step() -> None:
        from generator import generate
        generate()

    def _score_card_step() -> None:
        meta = load_latest_meta()
        if not meta:
            LOGGER.warning("[ScoreCard] No meta found. Skipping score card.")
            return
        from score_card import generate_for_resurrection
        date = str(meta.get("date", ""))
        folder = Path(RESURRECTION_BASE_FOLDER) / f"day-{date}" if date else None
        if folder and folder.exists():
            generate_for_resurrection(folder, meta)
        else:
            LOGGER.warning("[ScoreCard] Could not find folder for date %s.", date)

    def _stats_step() -> None:
        from stats import update_stats
        update_stats()

    def _readme_step() -> None:
        from readme_generator import update_readme
        update_readme()

    def _commenter_step() -> None:
        from issue_commenter import post_resurrection_comment
        meta = load_latest_meta()
        token = os.environ.get("GITHUB_TOKEN", "")
        if meta and token:
            post_resurrection_comment(meta, token)
        else:
            LOGGER.warning("[Commenter] Missing meta or token. Skipping.")

    results.append(run_step("GitHub Issue Scanner", _scanner_step))
    results.append(run_step("AI Analyzer", _analyzer_step))
    results.append(run_step("File Generator", _generator_step))
    results.append(run_step("Score Card Generator", _score_card_step))
    results.append(run_step("Stats Engine", _stats_step))
    results.append(run_step("README Generator", _readme_step))
    results.append(run_step("Original Issue Commenter", _commenter_step))

    meta = load_latest_meta()
    if not meta:
        LOGGER.error(
            "❌ Pipeline finished but no meta.json was found. "
            "Commit message vars will be empty. Aborting to prevent a bad commit."
        )
        sys.exit(1)

    export_commit_vars(meta)
    LOGGER.info("Pipeline complete. Steps: %d/%d passed.", sum(results), len(results))

    if not all(results):
        sys.exit(1)


if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    validate_env()
    run_pipeline()
