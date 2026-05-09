# [Feature Request] Add Support for const enum in TS

**Repository:** [babel/babel](https://github.com/babel/babel)
**Issue:** [babel/babel#8741](https://github.com/babel/babel/issues/8741)
**Reactions:** 161 👍
**Created:** 2018-09-20T16:29:33Z
**Last Activity:** 2021-11-03T04:03:25Z
**Labels:** area: typescript, outdated

---

## Original Description

## Feature Request
In the [docs](https://babeljs.io/docs/en/babel-plugin-transform-typescript), it says that:

> Does not support `const enum`s because those require type information to compile.

I don't believe that this is true. Babel should be able to transpile `const enum`s into objects, which will achieve the same functionality as typescript, through different transpiled output.

Given this code:

```ts
const enum Direction { Left, Right, Down, Up }
console.log(Direction.Down)
```

`tsc` would compile this to:
```js
console.log(2)
```

I propose that Babel compiles the enum to:

```js
const Direction = {
  Left: 0,
  Right: 1,
  Down: 2,
  Up: 3
}
console.log(Direction.Down)
```

Which functions the same as the `tsc` output.

A minifier like `terser`/`uglify` is able to transpile that output ☝️ to the same as the `tsc` output.

---

*Resurrected by Resurrection Bot 🧬*
