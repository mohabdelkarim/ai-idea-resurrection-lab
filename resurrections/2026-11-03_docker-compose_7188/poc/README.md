# Proof of Concept: Port conflict with multiple "host:<port range>:port" services

**Language:** go
**Estimated run time:** < 5 minutes

## Prerequisites

- Go 1.22+

## How to Run

```bash
go run main.go
```

## What This Demonstrates

Docker Compose should automatically resolve overlapping host port ranges to prevent container startup failures.
