# Proof of Concept: [feat] upstream nix requirements to nixpkgs

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

Tauri will maintain a Nix derivation in nixpkgs with dependencies matching the documentation.
