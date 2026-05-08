# add support for mercurial

**Repository:** [BurntSushi/ripgrep](https://github.com/BurntSushi/ripgrep)
**Issue:** [BurntSushi/ripgrep#6](https://github.com/BurntSushi/ripgrep/issues/6)
**Reactions:** 20 👍
**Created:** 2016-09-16T22:08:24Z
**Last Activity:** 2024-12-05T21:14:29Z
**Labels:** enhancement, help wanted

---

## Original Description

Mercurial is widely used enough that we should probably support it. Mercurial will actually be harder to do correctly than git, because an `.hgignore` file can support both regexes and globs. An `.hgignore` file can also specify _subincludes_, which include ignore patterns in a sub-directory (as opposed to `git`, which will read `.gitignore` files in sub-directories automatically).

Thankfully, `ripgrep` translates all globs to regexes, so we should be able to support Mercurial without too much trouble.

See: `hg help hgignore` and `hg help patterns`.


---

*Resurrected by Resurrection Bot 🧬*
