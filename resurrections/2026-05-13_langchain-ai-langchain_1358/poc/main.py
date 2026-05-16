"""
PoC: ValueError: Could not parse LLM output (langchain-ai/langchain#1358)

The root cause: MRKL / ConversationalReact agents use a strict regex to
parse "Action: ..." / "Action Input: ..." from LLM output. Open-source
models (flan-t5, Bloom) produce conversational responses that don't match
this format, causing ValueError.

The correct fix (and what LangChain eventually did): allow agents to
specify a custom OutputParser, and ship a more lenient parser for
non-instruction-tuned models.

This PoC demonstrates:
  1. The broken parser (strict regex) — crashes on casual LLM output
  2. The fixed parser (lenient fallback) — handles both formats
  3. A RouterOutputParser that picks the right strategy per model type

No LangChain or API key required — runs standalone.
To run:  python poc/main.py
"""

import re
from dataclasses import dataclass
from typing import Optional


# ---------------------------------------------------------------------------
# 1. Simulate LLM outputs from different model families
# ---------------------------------------------------------------------------

OPENAI_OUTPUT = """I need to look up the weather.
Action: search
Action Input: current weather in Athens"""

FLAN_T5_OUTPUT = """Assistant, how can I help you today?"""

BLOOM_OUTPUT = """Sure! I can help with that. What city are you asking about?"""


# ---------------------------------------------------------------------------
# 2. The ORIGINAL broken parser (mirrors the 2023 ConversationalReactAgent)
# ---------------------------------------------------------------------------

@dataclass
class AgentAction:
    action: str
    action_input: str

@dataclass
class AgentFinish:
    output: str


class StrictMRKLOutputParser:
    """Original parser — strict regex, crashes on open-source model output."""

    ACTION_RE = re.compile(r"Action: (.+?)\nAction Input: (.+)", re.DOTALL)

    def parse(self, llm_output: str):
        match = self.ACTION_RE.search(llm_output)
        if not match:
            # This is what caused #1358
            raise ValueError(f"Could not parse LLM output: {llm_output!r}")
        return AgentAction(action=match.group(1).strip(),
                           action_input=match.group(2).strip())


# ---------------------------------------------------------------------------
# 3. The FIXED parser — lenient fallback treats unparseable output as Final Answer
# ---------------------------------------------------------------------------

class LenientOutputParser:
    """
    Fixed parser: if strict Action/Input parsing fails, treat the whole
    output as a Final Answer instead of crashing. This matches what
    LangChain merged in the OutputParser refactor.
    """

    ACTION_RE = re.compile(r"Action: (.+?)\nAction Input: (.+)", re.DOTALL)
    FINAL_ANSWER_RE = re.compile(r"Final Answer: (.+)", re.DOTALL)

    def parse(self, llm_output: str):
        # Try structured action format first
        match = self.ACTION_RE.search(llm_output)
        if match:
            return AgentAction(action=match.group(1).strip(),
                               action_input=match.group(2).strip())
        # Try explicit Final Answer
        fa_match = self.FINAL_ANSWER_RE.search(llm_output)
        if fa_match:
            return AgentFinish(output=fa_match.group(1).strip())
        # Lenient fallback: treat entire output as final answer (key fix for #1358)
        return AgentFinish(output=llm_output.strip())


# ---------------------------------------------------------------------------
# 4. Router: pick parser based on model family
# ---------------------------------------------------------------------------

class RouterOutputParser:
    def __init__(self):
        self._strict = StrictMRKLOutputParser()
        self._lenient = LenientOutputParser()

    def parse(self, llm_output: str, model_family: str = "openai"):
        if model_family == "openai":
            return self._strict.parse(llm_output)
        return self._lenient.parse(llm_output)


# ---------------------------------------------------------------------------
# 5. Demo
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    strict = StrictMRKLOutputParser()
    lenient = LenientOutputParser()
    router = RouterOutputParser()

    print("=== StrictMRKLOutputParser (original broken behaviour) ===")
    try:
        result = strict.parse(OPENAI_OUTPUT)
        print(f"  OpenAI : OK -> Action={result.action!r}")
    except ValueError as e:
        print(f"  OpenAI : CRASH -> {e}")

    try:
        result = strict.parse(FLAN_T5_OUTPUT)
        print(f"  flan-t5: OK -> {result}")
    except ValueError as e:
        print(f"  flan-t5: CRASH (this is the #1358 bug) -> {e}")

    print()
    print("=== LenientOutputParser (fix) ===")
    for label, output in [("OpenAI", OPENAI_OUTPUT), ("flan-t5", FLAN_T5_OUTPUT), ("Bloom", BLOOM_OUTPUT)]:
        result = lenient.parse(output)
        kind = type(result).__name__
        if isinstance(result, AgentAction):
            print(f"  {label:8s}: {kind} -> action={result.action!r}")
        else:
            print(f"  {label:8s}: {kind} -> output={result.output[:60]!r}")

    print()
    print("=== RouterOutputParser ===")
    r1 = router.parse(OPENAI_OUTPUT, model_family="openai")
    r2 = router.parse(FLAN_T5_OUTPUT, model_family="huggingface")
    print(f"  OpenAI (strict)  : {type(r1).__name__} action={r1.action!r}")
    print(f"  flan-t5 (lenient): {type(r2).__name__} output={r2.output!r}")
