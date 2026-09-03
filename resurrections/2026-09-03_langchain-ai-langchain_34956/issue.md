# Enable Exporting Select Agent Metrics to Customer-facing Dashboards in Real-Time

**Repository:** [langchain-ai/langchain](https://github.com/langchain-ai/langchain)
**Issue:** [langchain-ai/langchain#34956](https://github.com/langchain-ai/langchain/issues/34956)
**Reactions:** 9 👍
**Created:** 2026-02-01T10:17:29Z
**Last Activity:** 2026-06-11T07:31:01Z
**Labels:** langchain, feature request, external

---

## Original Description

### Checked other resources

- [x] This is a feature request, not a bug report or usage question.
- [x] I added a clear and descriptive title that summarizes the feature request.
- [x] I used the GitHub search to find a similar feature request and didn't find it.
- [x] I checked the LangChain documentation and API reference to see if this feature already exists.
- [x] This is not related to the langchain-community package.

### Package (Required)

- [x] langchain
- [ ] langchain-openai
- [ ] langchain-anthropic
- [ ] langchain-classic
- [ ] langchain-core
- [ ] langchain-model-profiles
- [ ] langchain-tests
- [ ] langchain-text-splitters
- [ ] langchain-chroma
- [ ] langchain-deepseek
- [ ] langchain-exa
- [ ] langchain-fireworks
- [ ] langchain-groq
- [ ] langchain-huggingface
- [ ] langchain-mistralai
- [ ] langchain-nomic
- [ ] langchain-ollama
- [ ] langchain-perplexity
- [ ] langchain-prompty
- [ ] langchain-qdrant
- [ ] langchain-xai
- [ ] Other / not sure / general

### Feature Description

Langchain needs to enable exporting standard AI agent metrics (e.g., latency, token usage) to customer-facing dashboards for cost visibility, usage monitoring, etc.

### Use Case

Real use case: We have Langchain-based agent. The customer requires adding latency and token usage metrics to their dashboard.

Currently, these metrics can be found in Langsmith, but the latter isn't designed to be customer-facing and may expose debugging internals that will overhelm the customer.

We need to enable developers to plug in their own metrics exporter (e.g., Promotheus-based). Simultaneously, the exported metrics must be correlated with Langsmith (and optionally OpenTelemetry) traces to enable end-to-end observability and trace-level drill-downs.

### Proposed Solution

My proposed solution: https://github.com/langchain-ai/langchain/pull/34947

### Alternatives Considered

Developers must pull these metrics from Langsmith, which adds extra hops to the data flow and introduces additional failure points.

### Additional Context

_No response_

---

*Resurrected by Resurrection Bot 🧬*
