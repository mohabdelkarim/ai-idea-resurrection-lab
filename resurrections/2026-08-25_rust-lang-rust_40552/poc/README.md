# Proof of Concept: Enable --remap-path-prefix for absolute paths by default

**Language:** rust
**Estimated run time:** < 5 minutes

## Prerequisites

- Rust 1.75+ (`rustc`)

## How to Run

```bash
rustc main.rs -o main && ./main
```

## What This Demonstrates

Add a rustc flag that remaps absolute source paths to relative crate‑based paths by default.
