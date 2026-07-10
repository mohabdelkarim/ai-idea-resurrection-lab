# get_openai_callback not working when using Agent Executor after updating to latest version of Langchain

**Repository:** [langchain-ai/langchain](https://github.com/langchain-ai/langchain)
**Issue:** [langchain-ai/langchain#16798](https://github.com/langchain-ai/langchain/issues/16798)
**Reactions:** 22 👍
**Created:** 2024-01-30T18:34:08Z
**Last Activity:** 2026-01-22T11:26:07Z
**Labels:** help wanted

---

## Original Description

### Checked other resources

- [X] I added a very descriptive title to this issue.
- [X] I searched the LangChain documentation with the integrated search.
- [X] I used the GitHub search to find a similar question and didn't find it.
- [X] I am sure that this is a bug in LangChain rather than my code.

### Example Code

```python
class MyCustomAsyncHandler(AsyncCallbackHandler):
    async def on_llm_end(self, response: LLMResult, **kwargs: Any) -> None:
        """Run when chain ends running."""
        print("RESPONSE: ", response)
        print("Hi! I just woke up. Your llm is ending")


async def ask_assistant(input: str) -> str:
    prompt = PromptTemplate.from_template(prompt_raw)

    prompt = prompt.partial(
        language="Spanish",
        tools=render_text_description(tools),
        tool_names=", ".join([t.name for t in tools]),
    )

    llm = ChatOpenAI(
        temperature=0,
        model_name="gpt-4",
        openai_api_key=os.environ["OPENAI_API_KEY"],
        callbacks=[MyCustomAsyncHandler()],
    )
    llm_with_stop = llm.bind(stop=["\nObservation"])

    agent = (
        {
            "input": lambda x: x["input"],
            "agent_scratchpad": lambda x: format_log_to_str(x["intermediate_steps"]),
            "chat_history": lambda x: x["chat_history"],
        }
        | prompt
        | llm_with_stop
        | ReActSingleInputOutputParser()
    )

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
        clara_ai_output = clara_ai_resp["output"]

        print("CB: ", cb)

        return clara_ai_output, input, cb
```

### Error Message and Stack Trace (if applicable)

_No response_

### Description

I'm trying to use the get_openai_callback from langchain_community.callbacks to get the number of token and costs incurred in using the agent but I am getting zero on everything, as you can see here when I print.

![image](https://github.com/langchain-ai/langchain/assets/46487685/d728843a-6191-4f97-97e5-65431c02f98e)

I have also set up a custom callback handler to go deep into the issue and what I found is that ChatOpenAI from langchain_openai does not call ainvoke as ChatOpenAI langchain.chat_models did.

THank you for your help



### System Info

python 3.11.5

---

*Resurrected by Resurrection Bot 🧬*
