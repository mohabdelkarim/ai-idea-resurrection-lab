# {#range ...} block

**Repository:** [sveltejs/svelte](https://github.com/sveltejs/svelte)
**Issue:** [sveltejs/svelte#2968](https://github.com/sveltejs/svelte/issues/2968)
**Reactions:** 121 👍
**Created:** 2019-06-07T13:22:12Z
**Last Activity:** 2024-12-03T07:37:28Z
**Labels:** feature request, awaiting submitter, popular

---

## Original Description

Never thought I'd say this but I think we need range blocks — we've had so many questions along the lines of 'how do I iterate *n* times?'.

The usual answer is one of these...

```html
{#each Array(n) as _, i}
  <p>{i}</p>
{/each}
```

```html
{#each { length: n } as _, i}
  <p>{i}</p>
{/each}
```

...but neither is particularly satisfying.

Anyway, we're a compiler, so we can add this for free, if we want to. The only real question is syntax. We could emulate Ruby's range operator:

```html
<!-- 1,2,3,4,5 -->
{#range 1..5 as n}
  {n}
{/range}

<!-- 1,2,3,4 -->
{#range 1...5 as n}
  {n}
{/range}
```

`{#range 5 as n}` could be shorthand for `{#range 0...5 as n}`, perhaps.

Complications: Ruby's operator also handles decrementing ranges (`5...1`) and strings (`'a'...'z'` and `'z'...'a'`), so if we were to steal that syntax then presumably we should also support those.

Any thoughts?

---

*Resurrected by Resurrection Bot 🧬*
