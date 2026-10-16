# output shell completion script by `bat --completion <shell>` command

**Repository:** [sharkdp/bat](https://github.com/sharkdp/bat)
**Issue:** [sharkdp/bat#2057](https://github.com/sharkdp/bat/issues/2057)
**Reactions:** 15 👍
**Created:** 2022-02-02T15:24:57Z
**Last Activity:** 2025-01-08T01:05:12Z
**Labels:** feature-request, packaging/tooling

---

## Original Description

Currently the autocompletion script comes only with the source.

A better approach, would be something like `bat --completion=bash`.

Here is my current `bash_completion` script executed at login:

```bash
source <($HOME/.local/bin/helm completion bash)
source <($HOME/.local/bin/kustomize completion bash)
source <($HOME/.local/bin/pip completion --bash)
source <($HOME/.local/bin/stern --completion=bash)
source <($HOME/.local/node/bin/npm completion)
source $HOME/.local/bat/autocomplete/bat.bash # this can become `bat --completion=bash` 
```

---

*Resurrected by Resurrection Bot 🧬*
