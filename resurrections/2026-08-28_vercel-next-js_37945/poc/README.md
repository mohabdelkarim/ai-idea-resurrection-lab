# Proof of Concept: ISR fails to serve 404 pages once the page gets deleted if experimental isr memory cache size is set to 0

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

ISR memory cache disabled leads to stale pages instead of 404 after deletion.
