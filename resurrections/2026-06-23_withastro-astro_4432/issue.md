# Supporting CSS-in-JS

**Repository:** [withastro/astro](https://github.com/withastro/astro)
**Issue:** [withastro/astro#4432](https://github.com/withastro/astro/issues/4432)
**Reactions:** 55 👍
**Created:** 2022-08-22T23:13:00Z
**Last Activity:** 2023-11-21T20:07:19Z
**Labels:** - P2: nice to have

---

## Original Description

It's not super clear which CSS-in-JS libraries work, so I'm creating this issue as sort of a place to start the conversation and document the current status.

Here's a few popular libraries that I know about (will keep this list updated):

| Library           | Status             | Notes                                                                                                                                                                                                                                                                                                                                                                                                   |
| ----------------- | ------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| styled-components | 🟡 Partially works | Prod build errors with: `styled.div is not a function`. <br> Can be worked around with [`client:only`](https://docs.astro.build/en/reference/directives-reference/#clientonly) or by using [`buildSsrCjsExternalHeuristics`](https://vitejs.dev/guide/ssr.html#ssr-format) and [`ssr.noExternal`](https://vitejs.dev/config/ssr-options.html#ssr-noexternal) (will cause FOUC). |
| emotion           | 🟡 Partially works | Prod build errors with: `styled.div is not a function`. <br> Can be worked around with [`client:only`](https://docs.astro.build/en/reference/directives-reference/#clientonly) or by using [conditional default import](https://github.com/withastro/astro/issues/4432#issuecomment-1259062851) (will cause FOUC). Can also [patch `@astrojs/react`](https://github.com/withastro/astro/issues/4432#issuecomment-1259062851). |
| linaria           | 🟡 Partially works           | Prod build errors with: `Named export 'styled' not found`. <br> Can be worked around using [`buildSsrCjsExternalHeuristics`](https://vitejs.dev/guide/ssr.html#ssr-format) and [`ssr.noExternal`](https://vitejs.dev/config/ssr-options.html#ssr-noexternal) or by downgrading to v3.                                                                                                 |
| stitches          | 🟡 Partially works           | `<style>` tag for SSR needs to be in React component                                                                                                                                                                                                                                                                                                                                                    |
| typestyle         | ✅ Works           | -                                                                                         

---

*Resurrected by Resurrection Bot 🧬*
