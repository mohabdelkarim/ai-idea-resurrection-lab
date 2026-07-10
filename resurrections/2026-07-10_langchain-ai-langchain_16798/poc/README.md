# Proof of Concept: get_openai_callback not working when using Agent Executor after updating to latest version of Langchain

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

The get_openai_callback function does not accurately track token usage and costs when used with AgentExecutor in Langchain.
