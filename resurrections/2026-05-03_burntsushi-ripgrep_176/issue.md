# support searching across multiple lines

**Repository:** [BurntSushi/ripgrep](https://github.com/BurntSushi/ripgrep)
**Issue:** [BurntSushi/ripgrep#176](https://github.com/BurntSushi/ripgrep/issues/176)
**Reactions:** 61 👍
**Created:** 2016-10-13T21:31:20Z
**Last Activity:** 2021-12-01T14:11:33Z
**Labels:** enhancement, libripgrep

---

## Original Description

Say for example I'm trying to find instances of `click` that reside in a `listeners` block, like so:

```
listeners: {
    foo: ...
    click: ....
}
```

According to the Rust regex docs, I should be able to do: `rg '(?s)listeners.+click'`, but this doesn't seem to work. Does ripgrep not support multiline regex?


---

*Resurrected by Resurrection Bot 🧬*
