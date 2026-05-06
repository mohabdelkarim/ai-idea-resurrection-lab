# support searching compressed files using in-process decompression

**Repository:** [BurntSushi/ripgrep](https://github.com/BurntSushi/ripgrep)
**Issue:** [BurntSushi/ripgrep#225](https://github.com/BurntSushi/ripgrep/issues/225)
**Reactions:** 27 👍
**Created:** 2016-11-08T18:15:04Z
**Last Activity:** 2018-02-21T05:17:47Z
**Labels:** question, icebox

---

## Original Description

I'd like to use ripgrep for grepping log files, because it's faster then grep. But my logs are gzipped, and if I `zcat | rg` them I'll loose log filenames in output.

Also, would be great if bzip2 and xz decompressors will be supported too with automatic archive type detection.

---

*Resurrected by Resurrection Bot 🧬*
