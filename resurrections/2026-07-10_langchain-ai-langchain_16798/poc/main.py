import asyncio
from typing import Any, Dict, List, Optional
from langchain.agents import AgentExecutor, ReActSingleInputOutputParser
from langchain.chains import LLMChain
from langchain.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.callbacks import AsyncCallbackHandler, CallbackManagerForLLMRun
from langchain.llm_usage import get_openai_callback

class MyCustomAsyncHandler(AsyncCallbackHandler):
    async def on_llm_end(self, response: Any, **kwargs: Any) -> None:
        print("RESPONSE: ", response)
        print("Hi! I just woke up. Your llm is ending")

async def ask_assistant(input: str) -> str:
    prompt_raw = "Translate the input to Spanish: {input}"
    prompt = PromptTemplate.from_template(prompt_raw)

    llm = ChatOpenAI(
        temperature=0,
        model_name="gpt-4",
        openai_api_key="your_openai_api_key",
        callbacks=[MyCustomAsyncHandler()],
    )
    llm_with_stop = llm.bind(stop=["\nObservation"])

    agent = (
        {
            "input": lambda x: x["input"],
            "agent_scratchpad": lambda x: format_log_to_str(x["intermediate_steps"]),
        }
        | prompt
        | llm_with_stop
        | ReActSingleInputOutputParser()
    )

    tools = []  # Define your tools here
    memory = None  # Define your memory here
    agent_executor = AgentExecutor(
        agent=agent,
        tools=tools,
        verbose=True,
        memory=memory,
        max_execution_time=60,
        handle_parsing_errors=True,
    )

    with get_openai_callback() as cb:
        clara_ai_resp = await agent_executor.ainvoke({"input": input})
        clara_ai_output = clara_ai_resp.get("output", "")

        print("CB: ", cb)

        return clara_ai_output, input, cb

async def main():
    try:
        input_str = "Hello, how are you?"
        output, input_str, cb = await ask_assistant(input_str)
        print("Output: ", output)
    except Exception as e:
        print("Error: ", str(e))

asyncio.run(main())