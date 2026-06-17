# Proof of Concept: maybe an optimizable point for zadd operation

**Language:** python
**Estimated run time:** < 5 minutes

## Prerequisites

- Python 3.12+, pip install requirements

## How to Run

```bash
pip install -r requirements.txt
python main.py
```

## What This Demonstrates

Optimize Redis zadd operation for small score deltas by avoiding unnecessary node re-insertion.
