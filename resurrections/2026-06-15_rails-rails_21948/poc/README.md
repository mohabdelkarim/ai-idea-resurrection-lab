# Proof of Concept: CSRF protection prevents some webkit users from submitting forms

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

CSRF protection in Rails prevents form submission for some WebKit users due to browser caching and session cookie clearing.
