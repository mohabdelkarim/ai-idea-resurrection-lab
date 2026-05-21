# Support for Pydantic v2

**Repository:** [langchain-ai/langchain](https://github.com/langchain-ai/langchain)
**Issue:** [langchain-ai/langchain#6841](https://github.com/langchain-ai/langchain/issues/6841)
**Reactions:** 75 👍
**Created:** 2023-06-27T20:24:25Z
**Last Activity:** 2023-08-17T21:20:44Z
**Labels:** 

---

## Original Description

### Feature request

Currently, `langchain 0.0.217 depends on pydantic<2 and >=1`. Pydantic v2 is re-written in Rust and is between 5-50x faster than v1 depending on the use case. Given how much LangChain relies on Pydantic for both modeling and functional components, and given that FastAPI is now supporting (in beta) Pydantic v2, it'd be great to see LangChain handle a user-specified installation of Pydantic above v2. 

The following is an example of what happens when a user specifies installing Pydantic above v2. 

```bash
The conflict is caused by:
    The user requested pydantic==2.0b2
    fastapi 0.100.0b1 depends on pydantic!=1.8, !=1.8.1, <3.0.0 and >=1.7.4
    inflect 6.0.4 depends on pydantic>=1.9.1
    langchain 0.0.217 depends on pydantic<2 and >=1
```

### Motivation

Pydantic v2 is re-written in Rust and is between 5-50x faster than v1 depending on the use case. Given how much LangChain relies on Pydantic for both modeling and functional components, and given that FastAPI is now supporting (in beta) Pydantic v2, it'd be great to see LangChain handle a user-specified installation of Pydantic above v2. 

### Your contribution

Yes! I'm currently opening just an issue to document my request, and because I'm fairly backlogged. But I have contributed to LangChain in the past and would love to write a pull request to facilitate this in full. 

---

*Resurrected by Resurrection Bot 🧬*
