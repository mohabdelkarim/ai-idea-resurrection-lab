# maximum line length

**Repository:** [BurntSushi/ripgrep](https://github.com/BurntSushi/ripgrep)
**Issue:** [BurntSushi/ripgrep#129](https://github.com/BurntSushi/ripgrep/issues/129)
**Reactions:** 48 👍
**Created:** 2016-09-28T17:47:19Z
**Last Activity:** 2017-03-13T01:21:29Z
**Labels:** enhancement, help wanted, libripgrep

---

## Original Description

I'd like `ripgrep` to have the ability to either hide or trim lines that are very long. Some lines take up my entire screen and are borderline useless to look at. It's possible that finding an intelligent way to shorten them would be best, since my guess is that the actual matched text is much smaller than the full line. However, this is harder to implement.

I don't think this should be enabled by default. It seems a little surprising for `ripgrep` to hide lines like that. In general, I like the work flow of, "run a search, see huge lines, confirm that I don't care about them and run ripgrep again with an option to hide them." It may however be plausible to enable this limit if results are being dumped to a terminal (we already enable colors, line numbers and file headings).


---

*Resurrected by Resurrection Bot 🧬*
