# Proof of Concept: Search based on file timestamps (atime, ctime, mtime)

**Language:** rust
**Estimated run time:** < 5 minutes

## Prerequisites

- Rust 1.75+, cargo

## How to Run

```bash
rustc main.rs -o main
./main
```

## What This Demonstrates

Implement timestamp-based file search in fd, similar to find's -atime, -ctime, and -mtime flags.
