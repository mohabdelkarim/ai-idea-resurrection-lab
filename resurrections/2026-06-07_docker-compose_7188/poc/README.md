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

Docker Compose fails to start services with overlapping port ranges, causing port conflicts.
