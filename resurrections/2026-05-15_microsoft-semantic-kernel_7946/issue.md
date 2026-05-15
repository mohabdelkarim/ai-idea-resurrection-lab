# Python: .Net: OpenAI - Support response_format type of json_schema (Structured Outputs)

**Repository:** [microsoft/semantic-kernel](https://github.com/microsoft/semantic-kernel)
**Issue:** [microsoft/semantic-kernel#7946](https://github.com/microsoft/semantic-kernel/issues/7946)
**Reactions:** 20 👍
**Created:** 2024-08-07T01:17:44Z
**Last Activity:** 2025-04-29T03:08:52Z
**Labels:** .NET, java, ai connector, stale

---

## Original Description

<!-- ⚠️⚠️ Do Not Delete This! feature_request_template ⚠️⚠️ -->
<!-- Please read our Rules of Conduct: https://opensource.microsoft.com/codeofconduct/ -->
<!-- Please search existing issues to avoid creating duplicates. -->

<!-- Describe the feature you'd like. -->
The latest OpenAI models allow passing `json_schema` as the `response_format` `type` property, and supplying the schema itself under the `schema` property. This enforces conformance to the schema by validating output tokens, rather than best LLM effort.

Announced here: https://openai.com/index/introducing-structured-outputs-in-the-api/

This is obviously massively useful to any application using json output, especially when deserialising the json to C# types. 
Please consider adding support for these properties through the SemanticKernel abstractions and .Net client in the short term.

---

*Resurrected by Resurrection Bot 🧬*
