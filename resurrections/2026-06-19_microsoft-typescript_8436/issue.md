# umd module compiler option doesn't have a fallback for global namespace.

**Repository:** [microsoft/TypeScript](https://github.com/microsoft/TypeScript)
**Issue:** [microsoft/TypeScript#8436](https://github.com/microsoft/TypeScript/issues/8436)
**Reactions:** 86 👍
**Created:** 2016-05-03T13:27:09Z
**Last Activity:** 2025-10-23T16:46:55Z
**Labels:** Suggestion, Needs Proposal

---

## Original Description

Most umd patterns have a third fallback that allows exporting to the window.namesapace = export; As such the current umd module export is pretty broken when a huge number of users / library developers need to support all three.

``` js
(function(root, factory) {
  if (typeof define === 'function' && define.amd) {
    define(factory);
  } else if (typeof exports === 'object') {
    module.exports = factory(require, exports, module);
  } else {
    root.exceptionless = factory();
  }
}(this, function(require, exports, module) {}
```


---

*Resurrected by Resurrection Bot 🧬*
