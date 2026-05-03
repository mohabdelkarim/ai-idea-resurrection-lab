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
    "withastro/astro",
    "remix-run/remix",
    "tauri-apps/tauri",

    # 🟣 Tier 4 — AI/ML & Data Science (high demand, rapid evolution)
    "openai/openai-python",
    "langchain-ai/langchain",
    "microsoft/semantic-kernel",
    "run-llama/llama_index",
    "ollama/ollama",
    "ggerganov/llama.cpp",
    "open-webui/open-webui",
    "comfyanonymous/ComfyUI",
    "gradio-app/gradio",
    "streamlit/streamlit",

    # ⚪ Tier 5 — Dev tools & CLI (beloved by developers, lots of stale feature requests)
    "cli/cli",
    "charmbracelet/bubbletea",
    "nickel-lang/nickel",
    "BurntSushi/ripgrep",
    "sharkdp/bat",
    "sharkdp/fd",
    "ajeetdsouza/zoxide",
    "starship/starship",
    "zellij-org/zellij",
    "alacritty/alacritty",
]

MIN_UPVOTES = 5              # lowered from 20: cast a wider net
MONTHS_STALE_THRESHOLD = 12  # raised from 6: 12 months is a safer "abandoned" signal
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
    "langchain",
    "llama",
    "ollama",
    "openai",
    "rag",
    "embeddings",
    "agents",
    "fine-tuning",
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

# Single source of truth for abandoned labels — imported by scanner.py
ABANDONED_LABELS: frozenset[str] = frozenset({
    # Standard wontfix variants
    "wontfix",
    "wont fix",
    "won't fix",
    "wont-fix",
    # Stale / inactive
    "stale",
    "staled",
    "inactive",
    "no-activity",
    # Feature requests (closed without implementing)
    "enhancement",
    "feature",
    "feature-request",
    "feature request",
    "type: feature",
    "type:feature",
    "kind/feature",
    "kind: feature",
    # Someday/maybe
    "someday",
    "maybe",
    "future",
    "icebox",
    "backlog",
    # Declined/deferred
    "declined",
    "deferred",
    "not planned",
    "not-planned",
    "on hold",
    "on-hold",
    # Discussion/proposal (closed without resolution)
    "needs-discussion",
    "needs discussion",
    "proposal",
    "idea",
    "rfc",
    # Help wanted (abandoned, nobody picked it up)
    "help wanted",
    "help-wanted",
    # Awaiting feedback / more info (closed without response)
    "awaiting-more-feedback",
    "awaiting more feedback",
    "needs-more-info",
    "more-information-needed",
    # Status: closed as design / by-design
    "by design",
    "by-design",
    "as designed",
    "closed-as-design",
    # Repo-specific common patterns
    "resolution: by design",
    "resolution: wont fix",
    "status: abandoned",
    "status: declined",
})

HIGH_DEMAND_UPVOTES_OVERRIDE = 50  # lowered from 100: 50 reactions = bypass label check

POST_ORIGINAL_ISSUE_COMMENT = True
SCORE_CARD_FILENAME = "score_card.svg"
