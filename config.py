REPOS_TO_SCAN = [
    "facebook/react",
    "vuejs/vue",
    "microsoft/TypeScript",
    "nodejs/node",
    "python/cpython",
    "django/django",
    "pallets/flask",
    "psf/requests",
    "rust-lang/rust",
    "golang/go",
    "microsoft/vscode",
    "huggingface/transformers",
    "pytorch/pytorch",
]

MIN_UPVOTES = 50
MONTHS_STALE_THRESHOLD = 6
MAX_ISSUES_PER_REPO = 100
MAX_DAILY_RESURRECTIONS = 1
SCAN_INTERVAL_DAYS = 3

APPROVED_TECHNOLOGY_TAGS = [
    "WebAssembly",
    "Rust async",
    "Go generics",
    "Python 3.13",
    "React RSC",
    "TypeScript 6",
    "Deno 2",
    "Node ESM",
    "WASM components",
    "AI/LLM integration",
    "Edge Runtime",
]

RESURRECTION_BASE_FOLDER = "resurrections"
GRAVEYARD_FOLDER = "graveyard"
STATS_FOLDER = "stats"
STATS_FILE = "stats/progress.json"
VOTES_FILE = "stats/votes.json"
DIGEST_LOG_FILE = "stats/digest_log.json"
PIPELINE_LOG_FILE = "stats/pipeline_log.json"
TEMPLATES_FOLDER = "templates"

BOT_NAME = "Resurrection Bot 🧬"
BOT_EMAIL = "bot@resurrection-lab.dev"
