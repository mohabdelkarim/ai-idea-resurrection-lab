# Support multiple --exec <cmd> instances

**Repository:** [sharkdp/fd](https://github.com/sharkdp/fd)
**Issue:** [sharkdp/fd#406](https://github.com/sharkdp/fd/issues/406)
**Reactions:** 14 👍
**Created:** 2019-02-09T11:20:47Z
**Last Activity:** 2022-03-21T14:51:26Z
**Labels:** help wanted, feature-request

---

## Original Description

Sometimes I run a command in several different matching directories with --exec, but I would like to print each directory for each command that is executed without having to add an intermediate shell just to print the path.

Perhaps adding an option that would print the matched file-name as well as executing the command in `--exec`. I tried with multiple `--exec` but it is not allowed, the only workaround I found was to have an intermediate shell.

Here is an example (print the git-status in all matching git directories:
```
fd -HFtd .git -x git -C '{//}' status -s
```

I can imagine that there are other use cases where you would want to print the matched file you execute the `-x` command for.

---

*Resurrected by Resurrection Bot 🧬*
