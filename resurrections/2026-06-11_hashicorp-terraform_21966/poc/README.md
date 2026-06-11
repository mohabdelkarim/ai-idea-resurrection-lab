# Proof of Concept: `terraform show <plan>` "Backend reinitialization required" within subfolder

**Language:** go
**Estimated run time:** < 5 minutes

## Prerequisites

- Go 1.22+

## How to Run

```bash
go run main.go
```

## What This Demonstrates

Allow `terraform show` to work in subfolders without requiring backend reinitialization.
