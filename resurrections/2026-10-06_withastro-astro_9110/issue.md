# Cannot destructure react component props

**Repository:** [withastro/astro](https://github.com/withastro/astro)
**Issue:** [withastro/astro#9110](https://github.com/withastro/astro/issues/9110)
**Reactions:** 5 👍
**Created:** 2023-11-15T19:44:04Z
**Last Activity:** 2025-01-03T13:45:54Z
**Labels:** pkg: react, - P3: minor bug, needs discussion

---

## Original Description

### Astro Info

```block
Astro                    v3.5.4
Node                     v18.18.0
System                   Linux (x64)
Package Manager          unknown
Output                   static
Adapter                  none
Integrations             @astrojs/react
```


### If this issue only occurs in one browser, which browser is a problem?

_No response_

### Describe the Bug

When running `astro dev`, I got an error **"Cannot destructure property 'xxx' of 'undefined' as it is undefined"** when using the `map` method on React component props. It seems like this error has occurred before and has been resolved in #660 , but it's happening again. 
If I missed something, please let me know.

### What's the expected result?

no errors

### Link to Minimal Reproducible Example

https://stackblitz.com/edit/github-hrgerw

### Participation

- [ ] I am willing to submit a pull request for this issue.

---

*Resurrected by Resurrection Bot 🧬*
