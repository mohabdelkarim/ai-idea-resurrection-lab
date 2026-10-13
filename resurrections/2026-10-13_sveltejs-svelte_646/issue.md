# Optimising at the AST level

**Repository:** [sveltejs/svelte](https://github.com/sveltejs/svelte)
**Issue:** [sveltejs/svelte#646](https://github.com/sveltejs/svelte/issues/646)
**Reactions:** 10 👍
**Created:** 2017-06-16T13:27:50Z
**Last Activity:** 2024-09-23T00:54:36Z
**Labels:** feature request, perf, compiler

---

## Original Description

Second random thought after #645. In cases like [this](https://svelte.technology/repl?version=1.22.4&gist=4ad6df1f08729b203c45204336d7cce8)...

```html
{#if foo}
  <p>foo!</p>
{:else}
  <p>not foo!</p>
{/if}
```

...we have to create three blocks (`create_main_fragment`, `create_if_block` and `create_if_block_1`), totalling 74 LOC as of the current version. If we optimised it to the equivalent of this...

```html
<p>{foo ? 'foo!' : 'not foo!'}</p>
```

...we get the same result with one block (`create_main_fragment`) totalling 25 LOC, and there's less work to do to update things.

There are probably all sorts of optimisations like this we could perform. Might not be straightforward, but definitely worth investigating.

---

*Resurrected by Resurrection Bot 🧬*
