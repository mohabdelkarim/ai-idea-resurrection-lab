# Option to disable all Cloud and remote Search features

**Repository:** [ollama/ollama](https://github.com/ollama/ollama)
**Issue:** [ollama/ollama#12436](https://github.com/ollama/ollama/issues/12436)
**Reactions:** 7 👍
**Created:** 2025-09-28T08:10:42Z
**Last Activity:** 2025-10-12T12:36:08Z
**Labels:** feature request

---

## Original Description

I understand why Ollama added remote model loading, cloud hosting, and search support. It helps finance development and provides convenience for many users.

However, a core reason for using Ollama is strong privacy and the guarantee of running models locally without any unwanted remote connections (except explicitly configured tool calls). For users with this priority, it would be very valuable to have a configuration option that completely disables all remote/cloud features.

I’m aware that without a login or token these features do not activate. Still, an explicit “local-only” mode would act as a safeguard.

Example:
A second admin, a misconfiguration, or buggy software might introduce a token or cloud model without my knowledge.

Even if unintentional and non-malicious, this could break the privacy expectation.

An explicit toggle/setting to enforce local-only operation would provide additional peace of mind for privacy-conscious users.

---

*Resurrected by Resurrection Bot 🧬*
