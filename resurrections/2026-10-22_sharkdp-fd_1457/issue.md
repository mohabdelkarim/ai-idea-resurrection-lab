# New .git Handling has no opt out

**Repository:** [sharkdp/fd](https://github.com/sharkdp/fd)
**Issue:** [sharkdp/fd#1457](https://github.com/sharkdp/fd/issues/1457)
**Reactions:** 9 👍
**Created:** 2023-12-21T06:34:31Z
**Last Activity:** 2024-04-29T02:33:05Z
**Labels:** feature-request

---

## Original Description

I have the following code:

```
fd --type d --base-directory ~/Source -H '\.git' | sed 's|/.git||'
```
which lists all folders that contain a `.git` folder (basically a project search). This worked fine in 8.x.x but breaks in 9.x.x due to the breaking change of the .git handling.

Sadly there is no option to opt out for this. because --no-ignore-vcs does bring back all ignored files (so .terraform, .terragrunt-cache, .node-modules, ...) which I do not want. I just want to include ".git" but not everything .gitignore

How can this be achieved? Could you bring back the old behaviour with some cli flag?

---

*Resurrected by Resurrection Bot 🧬*
