# Add a (singular) `$prop` rune

**Repository:** [sveltejs/svelte](https://github.com/sveltejs/svelte)
**Issue:** [sveltejs/svelte#9241](https://github.com/sveltejs/svelte/issues/9241)
**Reactions:** 140 👍
**Created:** 2023-09-21T17:15:48Z
**Last Activity:** 2024-08-22T10:46:27Z
**Labels:** runes

---

## Original Description

### Describe the problem

This came up multiple times in the Discord server, so I figured I'd create an issue for it:
In v5's runes mode, the only way to declare props is by using the `$props` rune, like so:
```js
let { someProp = 'default' } = $props();
```
This looks good unless you're using TypeScript, in which case in order to type your props, you'll have to pass a type argument to `$props`, what this means in effect is that you'll be duplicating your prop names:
```ts
let { someProp = 'default' } = $props<{ someProp: string }>();
```
Needless to say this is not very pretty, feels a bit overly verbose, it gets even more problematic when you have many props:
```ts
let {
    foo = 'default',
    bar,
    buzz = 123,
} = $props<{
    foo: string;
    bar: number;
    buzz: number;
}>();
```
Here, you have to traverse quite a bit of distance with your eyes in order to find a specific prop's type (e.g. `bar`), because the destructured variable and the corresponding type could potentially be far from each other, and you'll have to "switch" your eyes to an entirely different "list", if you will.

In addition, this format yields a weird order of `name` => `default-value` => `name` => `type`, and when you compare all of this to the old way of declaring props with types, the difference becomes apparent:
```ts
export let foo: string = 'default';
export let bar: number;
export let buzz: number = 123;
```
Which is more concise, of course, but the order is more logical as well: `name` => `type` => `default-value`.

### Describe the proposed solution

Introduce a singular `$prop` rune, like so:
```ts
let someProp = $prop<string>('default');
```
Which, once again, is less verbose and has a more logical order of symbols; the type of each prop is always next to it on the same line, and you don't have to repeat the prop name.

### Alternatives considered

- Just using the `$props` rune, which suffers from the aforementioned problems.

### Importance

nice to have

---

*Resurrected by Resurrection Bot 🧬*
