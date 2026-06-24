# Proof of Concept: Ubuntu install error when rg is installed also

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

The installation of bat and ripgrep on Ubuntu 20.04 conflicts due to overlapping files.
