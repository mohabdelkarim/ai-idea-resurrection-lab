# Suggestion: Regex-validated string type

**Repository:** [microsoft/TypeScript](https://github.com/microsoft/TypeScript)
**Issue:** [microsoft/TypeScript#6579](https://github.com/microsoft/TypeScript/issues/6579)
**Reactions:** 1895 👍
**Created:** 2016-01-22T22:50:35Z
**Last Activity:** 2024-04-28T12:15:56Z
**Labels:** Suggestion, Needs Proposal, Domain: Literal Types

---

## Original Description

There are cases, where a property can not just be any string (or a set of strings), but needs to match a pattern.

``` typescript
let fontStyle: 'normal' | 'italic' = 'normal'; // already available in master
let fontColor: /^#([0-9a-f]{3}|[0-9a-f]{6})$/i = '#000'; // my suggestion
```

It's common practice in JavaScript to store color values in css notation, such as in the css style reflection of DOM nodes or various 3rd party libraries.

What do you think?


---

*Resurrected by Resurrection Bot 🧬*
