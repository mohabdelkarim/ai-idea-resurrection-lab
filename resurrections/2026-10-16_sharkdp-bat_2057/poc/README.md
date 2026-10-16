# Proof of Concept: output shell completion script by `bat --completion <shell>` command

**Language:** rust
**Estimated run time:** < 5 minutes

## Prerequisites

- Rust 1.75+ (`rustc`)

## How to Run

```bash
rustc main.rs -o main && ./main
```

## What This Demonstrates

bat can now generate shell completion scripts via a dedicated --completion option.
