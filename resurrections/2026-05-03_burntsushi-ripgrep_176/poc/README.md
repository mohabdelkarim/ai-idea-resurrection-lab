# Proof of Concept: support searching across multiple lines

**Language:** Rust  
**Estimated run time:** < 1 minute

## Prerequisites

- Rust 1.75+ with Cargo

## How to Run

```bash
cd resurrections/2026-05-03_burntsushi-ripgrep_176/poc
cargo run
```

## Expected Output

```
Match on line 1: listeners: {
Match on line 2:     foo: ...
Match on line 3:     click: ....
Done.
```

## What This Demonstrates

Uses the `grep-searcher` + `grep-regex` crates (the actual libraries that
power ripgrep internally) to perform a multiline regex search across a
text buffer. The `(?s)` flag enables dot-all mode so `.` matches newlines,
demonstrating that the feature is feasible with ripgrep's own search engine.

## Dependencies

| Crate | Role |
|---|---|
| `grep-regex` | Builds a `Matcher` from a regex pattern |
| `grep-searcher` | Runs the search over a byte slice or file |
| `grep-matcher` | Trait definitions used by both crates |
