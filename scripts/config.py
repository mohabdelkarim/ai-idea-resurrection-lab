# ---------------------------------------------------------------------------
# Repos to scan — curated list of high-traffic repos with many closed issues
# Prioritized by: issue volume, community size, viral potential
# ---------------------------------------------------------------------------
REPOS_TO_SCAN = [
    # 🔵 Tier 1 — Massive communities, highest viral potential
    "microsoft/vscode",
    "nodejs/node",
    "python/cpython",
    "rust-lang/rust",
    "golang/go",
    "microsoft/TypeScript",
    "facebook/react",
    "vuejs/vue",
    "torvalds/linux",
    "llvm/llvm-project",

    # 🟡 Tier 2 — Strong communities, great technical depth
    "vercel/next.js",
    "denoland/deno",
    "sveltejs/svelte",
    "django/django",
    "pallets/flask",
    "rails/rails",
    "docker/compose",
    "kubernetes/kubernetes",
    "neovim/neovim",
    "JetBrains/intellij-community",

    # 🟢 Tier 3 — Focused communities, niche but high engagement
    "huggingface/transformers",
    "pytorch/pytorch",
    "psf/requests",
    "expressjs/express",
    "babel/babel",
    "webpack/webpack",
    "vitejs/vite",
    "prettier/prettier",
    "eslint/eslint",
    "ohmyzsh/ohmyzsh",
    "ansible/ansible",
    "hashicorp/terraform",
    "grafana/grafana",
    "prometheus/prometheus",
    "redis/redis",
    "postgres/postgres",
    "supabase/supabase",
    "withastro/astro",       # fixed: was astro-build/astro
    "remix-run/remix",
    "tauri-apps/tauri",
]

MIN_UPVOTES = 20
MONTHS_STALE_THRESHOLD = 6
SCAN_PAGES_PER_REPO = 5
MAX_ISSUES_PER_REPO = 500
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
    "typescript",
    "python",
    "rust",
    "go",
    "javascript",
    "react",
    "node",
    "vscode-api",
    "vscode",
    "git",
    "extension",
    "cli",
    "api",
    "llm",
    "wasm",
    "webassembly",
    "async",
    "generics",
    "testing",
    "performance",
    "compiler",
    "lsp",
    "tree-sitter",
    "ui",
    "ux",
    "dx",
    "devtools",
    "kubernetes",
    "docker",
    "terraform",
    "ansible",
    "redis",
    "postgres",
    "graphql",
    "grpc",
    "websocket",
    "http",
    "css",
    "html",
    "svg",
    "accessibility",
    "i18n",
    "security",
    "auth",
    "oauth",
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

ABANDONED_LABELS = {"wontfix", "stale", "someday", "help wanted", "enhancement"}
HIGH_DEMAND_UPVOTES_OVERRIDE = 100

POST_ORIGINAL_ISSUE_COMMENT = True
SCORE_CARD_FILENAME = "score_card.svg"
