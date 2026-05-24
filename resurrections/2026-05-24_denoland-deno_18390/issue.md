# Feature Request: Importing a `js` file could fall back to `ts` file in a `ts` file

**Repository:** [denoland/deno](https://github.com/denoland/deno)
**Issue:** [denoland/deno#18390](https://github.com/denoland/deno/issues/18390)
**Reactions:** 9 👍
**Created:** 2023-03-23T16:03:43Z
**Last Activity:** 2025-04-23T19:27:34Z
**Labels:** declined

---

## Original Description

### Discussed in https://github.com/denoland/deno/discussions/18293

<div type='discussions-op-text'>

<sup>Originally posted by **Conaclos** March 20, 2023</sup>
Hi!

One thing that prevents me from using _Deno_ for my TypeScript projects is the incompatibility of Deno with other tools. in particular _ESbuild_ and _TSC_.

I use _ESbuild_ and _TSC_ to transpile my projects for npm and the browser. ESbuild and TSC do not change the extension of import paths. That's mean we have to use js extension to import a TypeScript file.

It could be nice to implement a very simple resolution strategy for _Deno_: in a TypeScript file (file ending with ts extension): an import path ending with a _js_ extension is resolved to the same file, but ending with a ts extension if the _js_ file does not exist.

```ts
// a.ts
import * as b from "./b.js" // resolves to "./b.js" or "./b.ts" if "./b.js" does not exist
...
```


</div>

---

*Resurrected by Resurrection Bot 🧬*
