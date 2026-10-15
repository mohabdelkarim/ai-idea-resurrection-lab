# Proof of Concept: Prometheus docker container shouldn't run as user nobody

**Language:** go
**Estimated run time:** < 5 minutes

## Prerequisites

- Go 1.22+

## How to Run

```bash
go run main.go
```

## What This Demonstrates

Allow the Prometheus Docker image to run with a configurable non‑root user ID.
