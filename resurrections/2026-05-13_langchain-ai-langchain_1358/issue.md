# ValueError: Could not parse LLM output:

**Repository:** [langchain-ai/langchain](https://github.com/langchain-ai/langchain)
**Issue:** [langchain-ai/langchain#1358](https://github.com/langchain-ai/langchain/issues/1358)
**Reactions:** 123 👍
**Created:** 2023-03-01T08:50:18Z
**Last Activity:** 2024-06-30T16:02:40Z
**Labels:** 

---

## Original Description

`agent_chain = initialize_agent( tools=tools, llm= HuggingFaceHub(repo_id="google/flan-t5-xl"), agent="conversational-react-description", memory=memory, verbose=False)

agent_chain.run("Hi")`

**throws error. This happens with Bloom as well. Agent only with OpenAI is only working well.**

`_(self, inputs, return_only_outputs)
    140 except (KeyboardInterrupt, Exception) as e:
    141     self.callback_manager.on_chain_error(e, verbose=self.verbose)
--> 142     raise e
    143 self.callback_manager.on_chain_end(outputs, verbose=self.verbose)
...
---> 83     raise ValueError(f"Could not parse LLM output: "{llm_output}")
     84 action = match.group(1)
     85 action_input = match.group(2)

ValueError: Could not parse LLM output: Assistant, how can I help you today?`

---

*Resurrected by Resurrection Bot 🧬*
