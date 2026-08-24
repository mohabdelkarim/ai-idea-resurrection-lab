# Add a new `type Awaitable<T> = T | PromiseLike<T>`

**Repository:** [microsoft/TypeScript](https://github.com/microsoft/TypeScript)
**Issue:** [microsoft/TypeScript#31394](https://github.com/microsoft/TypeScript/issues/31394)
**Reactions:** 72 👍
**Created:** 2019-05-14T12:27:11Z
**Last Activity:** 2024-08-21T15:42:02Z
**Labels:** Needs Investigation

---

## Original Description

## Search Terms

- `awaitable`

## Suggestion

Add an awaitable type for values that will be awaited.

```ts
type Awaitable<T> = T | PromiseLike<T>;
```

This is based on [my question and a comment on StackOverflow](https://stackoverflow.com/questions/56021581/awaitable-type-in-typescript#comment98890590_56021581)

## Use Cases

Two use cases come in mind immediately:

1. A function accepts a callback that may either return a value synchronously, or may return a promise value. This will then probably be awaited.
2. This is more of a specific version of 1, but this would be the return type of `Promise.then()` / `Promise.catch` / `Promise.finally` callbacks.

Also, this type could replace all 1334 occurrences that come up when running `git grep '| Promise'` in the current TypeScript code base.

## Examples

Callback example:

```ts
async function logAnswer(getAnswer: () => Awaitable<number>): Promise<void> {
  const answer = await getAnswer();
  console.log(answer);
}

logAnswer(() => 42);
logAnswer(() => Promise.resolve(42));
```

Promise example:

```ts
Promise.resolve('Hello, world!').then(
  // This type annotation is silly. This is really just to show promise callbacks should accept `Awaitable<T>`.
  (hello): Awaitable<string> => {
    console.log(hello);
    return hello;
  },
);
```

## Checklist

My suggestion meets these guidelines:

* [x] This wouldn't be a breaking change in existing TypeScript/JavaScript code
* [x] This wouldn't change the runtime behavior of existing JavaScript code
* [x] This could be implemented without emitting different JS based on the types of the expressions
* [x] This isn't a runtime feature (e.g. library functionality, non-ECMAScript syntax with JavaScript output, etc.)
* [x] This feature would agree with the rest of [TypeScript's Design Goals](https://github.com/Microsoft/TypeScript/wiki/TypeScript-Design-Goals).



---

*Resurrected by Resurrection Bot 🧬*
