# Proof of Concept: Memory usage spikes during WAL replay to more than normal usage

**Language:** go
**Estimated run time:** < 5 minutes

## Prerequisites

- Go 1.22+

## How to Run

```bash
go run main.go
```

## What This Demonstrates

Prometheus experiences high memory usage during WAL replay on startup.
