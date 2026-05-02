# ---------------------------------------------------------------------------
# Repos to scan — curated list of high-traffic repos with many closed issues
# Prioritized by: issue volume, community size, viral potential
# ---------------------------------------------------------------------------
REPOS_TO_SCAN = [
    # 🔵 Tier 1 — Massive communities, highest viral potential
    "microsoft/vscode",          # 160k+ issues, huge dev audience
    "nodejs/node",               # 40k+ issues, Node.js ecosystem
    "python/cpython",            # 90k+ issues, Python core
    "rust-lang/rust",            # 50k+ issues, systems programming
    "golang/go",                 # 30k+ issues, Go language
    "microsoft/TypeScript",      # 30k+ issues, TS ecosystem
    "facebook/react",            # 12k+ issues, frontend
    "vuejs/vue",                 # 10k+ issues, frontend
    "torvalds/linux",            # kernel — legendary issues
    "llvm/llvm-project",         # compiler infrastructure

    # 🟡 Tier 2 — Strong communities, great technical depth
    "vercel/next.js",            # 20k+ issues, React framework
    "denoland/deno",             # 3k+ issues, modern JS runtime
    "sveltejs/svelte",           # 4k+ issues, rising frontend
    "django/django",             # Python web framework
    "pallets/flask",             # Python micro-framework
    "rails/rails",               # Ruby on Rails
    "docker/compose",            # container tooling
    "kubernetes/kubernetes",     # k8s orchestration
    "neovim/neovim",             # editor — passionate community
    "JetBrains/intellij-community",  # IDE tooling

    # 🟢 Tier 3 — Focused communities, niche but high engagement
    "huggingface/transformers",  # AI/ML ecosystem
    "pytorch/pytorch",           # deep learning
    "psf/requests",              # Python HTTP
    "expressjs/express",         # Node.js web framework
    "babel/babel",               # JS transpiler
    "webpack/webpack",           # bundler
    "vitejs/vite",               # modern build tool
    "prettier/prettier",         # code formatter
    "eslint/eslint",             # JS linter
    "ohmyzsh/ohmyzsh",           # shell tooling
    "ansible/ansible",           # DevOps automation
    "hashicorp/terraform",       # infrastructure as code
    "grafana/grafana",           # observability
    "prometheus/prometheus",     # metrics
    "redis/redis",               # in-memory DB
    "postgres/postgres",         # relational DB
    "supabase/supabase",         # Firebase alternative
    "astro-build/astro",         # modern web framework
    "remix-run/remix",           # full-stack React
    "tauri-apps/tauri",          # desktop apps with Rust
]

MIN_UPVOTES = 20
MONTHS_STALE_THRESHOLD = 6
SCAN_PAGES_PER_REPO = 5
MAX_ISSUES_PER_REPO = 500
MAX_DAILY_RESURRECTIONS = 1
SCAN_INTERVAL_DAYS = 3

# These are the canonical display names for tech tags.
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

# ---------------------------------------------------------------------------
# Issue commenter settings
# ---------------------------------------------------------------------------
POST_ORIGINAL_ISSUE_COMMENT = True
SCORE_CARD_FILENAME = "score_card.svg"
