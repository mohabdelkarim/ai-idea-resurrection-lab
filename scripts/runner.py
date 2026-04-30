from __future__ import annotations

import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import RESURRECTION_BASE_FOLDER, STATS_FILE, VOTES_FILE


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
        LOGGER.debug("GITHUB_ENV is not set. Skipping export for %s.", key)
        return

    safe_value = value.replace("\r", " ").replace("\n", " ").strip()
    path = Path(env_file)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(f"{key}={safe_value}\n")

