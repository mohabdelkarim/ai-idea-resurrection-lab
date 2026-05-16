# Proof of Concept: Remove restrictions of `gh pr view --json files`

**Language:** go
**Estimated run time:** < 5 minutes

## Prerequisites

- Go 1.22+

## How to Run

```bash
go run main.go
```

## What This Demonstrates

Remove the 100 record limit for 'gh pr view --json files' by implementing GraphQL pagination.
