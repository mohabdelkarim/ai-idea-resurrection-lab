# Feature Request: Idle model unload timeout (router mode / config.ini)

**Repository:** [ggerganov/llama.cpp](https://github.com/ggml-org/llama.cpp)
**Issue:** [ggerganov/llama.cpp#18189](https://github.com/ggml-org/llama.cpp/issues/18189)
**Reactions:** 15 👍
**Created:** 2025-12-19T01:15:59Z
**Last Activity:** 2026-05-03T13:11:56Z
**Labels:** enhancement, stale

---

## Original Description

### Prerequisites

- [x] I am running the latest code. Mention the version if possible as well.
- [x] I carefully followed the [README.md](https://github.com/ggml-org/llama.cpp/blob/master/README.md).
- [x] I searched using keywords relevant to my issue to make sure that I am creating a new issue that is not already open (or closed).
- [x] I reviewed the [Discussions](https://github.com/ggml-org/llama.cpp/discussions), and have a new and useful enhancement to share.

### Feature Description

It would be great if llama-server when run in router mode and/or with a config.ini could unload models that have been idle for a given time.

For example, you could default it to 300 (seconds) and have models that haven't performed any inference in 5 minutes be unloaded to free up resources.

### Motivation

Models current sit loaded until the max loaded models are met, using up system resources.

[llama-swap provides](https://github.com/mostlygeek/llama-swap#configuration) this as a `ttl` setting.

Somewhat related:
- https://github.com/ggml-org/llama.cpp/issues/11703
- https://github.com/ggml-org/llama.cpp/issues/4598

### Possible Implementation

```ini
unload-idle-seconds = 300

[some-custom-important-model]
m = /models/custom.gguf
unload-idle-seconds = 3600
```

```bash
llama-server --unload-idle-seconds 300 --models-dir /models
```


---

*Resurrected by Resurrection Bot 🧬*
