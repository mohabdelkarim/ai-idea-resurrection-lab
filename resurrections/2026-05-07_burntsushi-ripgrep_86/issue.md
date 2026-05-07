# invoke a pager to display results

**Repository:** [BurntSushi/ripgrep](https://github.com/BurntSushi/ripgrep)
**Issue:** [BurntSushi/ripgrep#86](https://github.com/BurntSushi/ripgrep/issues/86)
**Reactions:** 27 👍
**Created:** 2016-09-25T17:07:40Z
**Last Activity:** 2025-10-24T18:39:07Z
**Labels:** enhancement, wontfix

---

## Original Description

Just tried the tool, it's great (as is the blostpost btw). I'm usually using `grep -r foo | less -R` for searching (with an alias to get colored output), since there might be several pages of results; `rg` coloring is nice but is lost if piped into a pager. Would it make sense to invoke a pager automatically if the tool detects that its output is not piped?


---

*Resurrected by Resurrection Bot 🧬*
