from __future__ import annotations

import logging
import os
import sys
from pathlib import Path
from typing import Any, Callable

from config import RESURRECTION_BASE_FOLDER, STATS_FILE, VOTES_FILE


sys.path.insert(0, str(Path(__file__).parent))


logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
LOGGER = logging.getLogger(__name__)


REQUIRED_ENV_VARS = (
    "GITHUB_TOKEN",
    "OPENAI_API_KEY",
    "DIGEST_FROM_EMAIL",
    "DIGEST_TO_EMAIL",
    "DIGEST_SMTP_HOST",
    "DIGEST_SMTP_USER",
    "DIGEST_SMTP_PASSWORD",
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
        LOGGER.debug("GITHUB_ENV is not set. Skipping export for %s.", key)
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
    try:
        candidates = sorted(base.glob("day-*/meta.json"), reverse=True)
    except Exception as error:
        LOGGER.error("Failed searching for latest meta.json: %s", error)
        return {}

    if not candidates:
        LOGGER.warning("No resurrection meta.json files found under %s", base)
        return {}

    latest = candidates[0]
    try:
        import json

        with latest.open("r", encoding="utf-8") as handle:
            parsed = json.load(handle)
        if isinstance(parsed, dict):
            return parsed
        LOGGER.warning("Latest meta file is not a JSON object: %s", latest)
        return {}
    except Exception as error:
        LOGGER.error("Failed reading latest meta.json %s: %s", latest, error)
        return {}


def export_commit_vars(meta: dict[str, Any]) -> None:
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

    def _stats_step() -> None:
        from stats import update_stats

        update_stats()

    def _readme_step() -> None:
        from readme_generator import update_readme

        update_readme()

    def _vote_step() -> None:
        from vote_manager import run_vote
        from stats import load_progress

        progress = load_progress()
        last = progress.get("last_resurrection") or {}
        token = os.environ.get("GITHUB_TOKEN", "")
        if last:
            run_vote(last, token)
        else:
            LOGGER.warning("No resurrection found for vote.")

    results.append(run_step("GitHub Issue Scanner", _scanner_step))
    results.append(run_step("AI Analyzer", _analyzer_step))
    results.append(run_step("File Generator", _generator_step))
    results.append(run_step("Stats Engine", _stats_step))
    results.append(run_step("README Generator", _readme_step))
    results.append(run_step("Community Vote", _vote_step))

    meta = load_latest_meta()
    export_commit_vars(meta)
    LOGGER.info("Pipeline complete.")

    if not all(results):
        sys.exit(1)


if __name__ == "__main__":
    from dotenv import load_dotenv

    load_dotenv()
    validate_env()
    run_pipeline()
