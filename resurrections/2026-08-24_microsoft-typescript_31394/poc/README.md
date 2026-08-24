# Proof of Concept: Add a new `type Awaitable<T> = T | PromiseLike<T>`

**Language:** typescript
**Estimated run time:** < 5 minutes

## Prerequisites

- Node.js 20+
- Optional: `npm install` if you add a package.json

## How to Run

```bash
npx --yes ts-node main.ts
```

## What This Demonstrates

Introduce a global Awaitable<T> alias to simplify typing of synchronous or promise-returning values.
