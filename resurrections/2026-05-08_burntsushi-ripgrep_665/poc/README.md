# Proof of Concept: `--file-url` flag for ripgrep

**Language:** Rust (clap v4, url v2, walkdir v2)  
**Estimated run time:** < 2 minutes

## What This Demonstrates

Adds a `--file-url` flag that prints matched file paths as `file://` URLs instead of plain paths.  
Terminals that support **OSC 8 hyperlinks** (Warp, Ghostty, iTerm2, VS Code integrated terminal)  
will render these as clickable links that jump directly to the file + line number.

Example output without `--file-url`:
```
src/main.rs:42:    let result = compute();
```

Example output with `--file-url`:
```
file:///home/user/project/src/main.rs#L42:    let result = compute();
```

## Key fixes vs naive implementation

- Uses `fs::canonicalize()` before `Url::from_file_path()` — relative paths would produce invalid `file://` URLs
- Uses `walkdir` for recursive directory traversal (matches real rg behaviour)
- Uses clap v4 derive API — not the deprecated v2 `App::new`/`Arg::with_name`
- Skips binary files gracefully via `read_to_string` error handling

## Prerequisites

- Rust 1.75+ and Cargo

## How to Run

```bash
# from the poc/ directory
cargo run -- "TODO" /path/to/your/project
cargo run -- "TODO" /path/to/your/project --file-url
```
