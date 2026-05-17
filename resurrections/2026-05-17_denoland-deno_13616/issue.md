# [fmt] Option to remove semicolons

**Repository:** [denoland/deno](https://github.com/denoland/deno)
**Issue:** [denoland/deno#13616](https://github.com/denoland/deno/issues/13616)
**Reactions:** 52 👍
**Created:** 2022-02-07T17:58:43Z
**Last Activity:** 2023-01-26T20:57:49Z
**Labels:** suggestion, deno fmt

---

## Original Description

Hi!

A lot of JavaScript and TypeScript projects don't use semicolons. Some famous style conventions such as [StandardJS](https://standardjs.com/) prohibit their use (except when needed).

I suggest to add an option `useSemicolon` that defaults to `true` and can be turned off in order to remove automatically insertable semicolons. When turned off this option set [dprint's semicolon option](https://dprint.dev/plugins/typescript/config/) to `asi`.

I think it is an option in the same vein as `useTabs` and `indentWidth`: for some people this improves code readability.

---

*Resurrected by Resurrection Bot 🧬*
