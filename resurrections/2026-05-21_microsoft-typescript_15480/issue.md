# Suggestion: Range as Number type

**Repository:** [microsoft/TypeScript](https://github.com/microsoft/TypeScript)
**Issue:** [microsoft/TypeScript#15480](https://github.com/microsoft/TypeScript/issues/15480)
**Reactions:** 1403 👍
**Created:** 2017-04-30T12:47:27Z
**Last Activity:** 2023-10-23T16:21:31Z
**Labels:** Suggestion, In Discussion

---

## Original Description

When defining a type one can specify multiple numbers separated by `|`.

```ts
type TTerminalColors = 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 | 12 | 13 | 14 | 15;
```

Allow to specify number types as ranges, instead of listing each number:

```ts
type TTerminalColors = 0..15;
type TRgbColorComponent = 0..255;
type TUInt = 0..4294967295;
```

Maybe use `..` for integers and `...` for floats.

```ts
interface Math {
  random(): 0...1
}

type RandomDice = 1..6;

const roll: RandomDice = Math.floor(Math.random() * 6);
// Error: -------------------------^ Maybe use Math.ceil()?
```

---

*Resurrected by Resurrection Bot 🧬*
