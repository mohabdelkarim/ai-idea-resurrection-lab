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

# Steps that MUST succeed for the pipeline to be considered healthy.
# If any of these fail, the pipeline exits with code 1.
CRITICAL_STEPS = {
    "GitHub Issue Scanner",
    "AI Analyzer",
    "File Generator",
}


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
    LOGGER.info("\u25b6 Running: %s", step_name)
    try:
        fn()
    except Exception as error:
        LOGGER.error("\u274c %s failed: %s", step_name, error)
        return False
    LOGGER.info("\u2705 %s completed.", step_name)
    return True


def load_latest_meta() -> dict[str, Any]:
    """
    Load the meta.json from the most recently MODIFIED resurrection folder.
    Uses mtime instead of alphabetical sort so the truly latest run is always returned,
    even when two resurrections happen on the same calendar day for different repos.
    """
    base = Path(RESURRECTION_BASE_FOLDER)
    meta_files = list(base.glob("*/meta.json"))
    if not meta_files:
        LOGGER.warning("No resurrection meta.json files found under %s", base)
        return {}

    # Sort by modification time, most recent first
    meta_files.sort(key=lambda p: p.stat().st_mtime, reverse=True)
    latest = meta_files[0]
    LOGGER.info("Loading latest meta from: %s", latest)
    try:
        with latest.open("r", encoding="utf-8") as handle:
            parsed = json.load(handle)
        return parsed if isinstance(parsed, dict) else {}
    except Exception as error:
        LOGGER.error("Failed reading latest meta.json %s: %s", latest, error)
        return {}


def _find_resurrection_folder(meta: dict[str, Any]) -> Path | None:
    """
    Locate the resurrection folder for a given meta dict.
    Folders follow the pattern YYYY-MM-DD_<repo-slug>_<issue_number>.
    We match by repo + issue_number from the meta, searching all subdirs,
    so we never depend on a hardcoded pattern that may not exist.
    """
    base = Path(RESURRECTION_BASE_FOLDER)
    if not base.exists():
        return None

    repo = str(meta.get("repo", ""))
    issue_number = str(meta.get("issue_number", ""))

    # Primary strategy: match meta.json content inside each subdir
    for child in sorted(base.iterdir(), reverse=True):
        if not child.is_dir():
            continue
        meta_path = child / "meta.json"
        if not meta_path.exists():
            continue
        try:
            child_meta = json.loads(meta_path.read_text(encoding="utf-8", errors="ignore"))
            if (
                str(child_meta.get("repo", "")) == repo
                and str(child_meta.get("issue_number", "")) == issue_number
            ):
                return child
        except (json.JSONDecodeError, OSError):
            continue

    # Fallback: the most recently modified folder that contains a meta.json
    meta_files = list(base.glob("*/meta.json"))
    if meta_files:
        meta_files.sort(key=lambda p: p.stat().st_mtime, reverse=True)
        LOGGER.warning(
            "[ScoreCard] Exact folder match failed for %s#%s — falling back to latest folder.",
            repo, issue_number,
        )
        return meta_files[0].parent

    return None


def export_commit_vars(meta: dict[str, Any]) -> None:
    if not meta:
        LOGGER.error(
            "\u26a0\ufe0f  export_commit_vars called with empty meta — "
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
    # _temp_file_path holds the path returned by analyze() and is passed
    # explicitly to generate() — no shared global state between the two.
    _temp_file_path: list[str] = [""]

    results: dict[str, bool] = {}

    def _scanner_step() -> None:
        from scanner import scan_issues
        scan_issues()

    def _analyzer_step() -> None:
        from analyzer import analyze
        path = analyze()
        if not path:
            raise RuntimeError(
                "Analyzer returned no temp file path — "
                "no unresurrected issues found or all repos are in cooldown."
            )
        _temp_file_path[0] = path
        LOGGER.info("[Runner] Analyzer wrote temp file: %s", path)

    def _generator_step() -> None:
        from generator import generate
        path = _temp_file_path[0]
        if not path:
            raise RuntimeError(
                "Generator called but no temp file path is set. "
                "Analyzer step may have been skipped or failed."
            )
        generate(temp_file_path=path)

    def _score_card_step() -> None:
        meta = load_latest_meta()
        if not meta:
            LOGGER.warning("[ScoreCard] No meta found. Skipping score card.")
            return
        from score_card import generate_for_resurrection
        folder = _find_resurrection_folder(meta)
        if folder and folder.exists():
            generate_for_resurrection(folder, meta)
        else:
            LOGGER.warning(
                "[ScoreCard] Could not find resurrection folder for %s#%s.",
                meta.get("repo", "?"), meta.get("issue_number", "?"),
            )

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

    steps = [
        ("GitHub Issue Scanner", _scanner_step),
        ("AI Analyzer",          _analyzer_step),
        ("File Generator",       _generator_step),
        ("Score Card Generator", _score_card_step),
        ("Stats Engine",         _stats_step),
        ("README Generator",     _readme_step),
        ("Original Issue Commenter", _commenter_step),
    ]

    for step_name, step_fn in steps:
        ok = run_step(step_name, step_fn)
        results[step_name] = ok
        # Abort early if a critical step fails — no point continuing
        if not ok and step_name in CRITICAL_STEPS:
            LOGGER.error(
                "\u274c Critical step '%s' failed — aborting pipeline.", step_name
            )
            sys.exit(1)

    meta = load_latest_meta()
    if not meta:
        LOGGER.error(
            "\u274c Pipeline finished but no meta.json was found. "
            "Commit message vars will be empty. Aborting to prevent a bad commit."
        )
        sys.exit(1)

    export_commit_vars(meta)

    critical_ok = all(results.get(s, False) for s in CRITICAL_STEPS)
    non_critical_failures = [
        name for name, ok in results.items()
        if not ok and name not in CRITICAL_STEPS
    ]
    if non_critical_failures:
        LOGGER.warning(
            "[Runner] Non-critical steps failed (pipeline still succeeds): %s",
            ", ".join(non_critical_failures),
        )

    total = len(results)
    passed = sum(results.values())
    LOGGER.info("Pipeline complete. Steps: %d/%d passed.", passed, total)

    if not critical_ok:
        sys.exit(1)


if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    validate_env()
    run_pipeline()
