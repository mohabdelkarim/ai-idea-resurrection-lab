# Proof of Concept: Add `rustc --fatal` which stops at the first build error

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

Add a rustc flag to exit after the first build error.
