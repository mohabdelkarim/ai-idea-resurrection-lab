# Proof of Concept: Tainted `null_resource` with `destroy provisioner` does not run the destroy command.

**Language:** go
**Estimated run time:** < 5 minutes

## Prerequisites

- Go 1.22+

## How to Run

```bash
go run main.go
```

## What This Demonstrates

Tainted null_resource destroy provisioner should execute during re-apply after taint.
