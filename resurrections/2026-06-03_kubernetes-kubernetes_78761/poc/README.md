# Proof of Concept: HPA doesn't scale down to minReplicas even though metric is under target

**Language:** go
**Estimated run time:** < 5 minutes

## Prerequisites

- Go 1.22+

## How to Run

```bash
go run main.go
```

## What This Demonstrates

HPA fails to scale down to minReplicas when metric is under target, causing inefficient resource usage.
