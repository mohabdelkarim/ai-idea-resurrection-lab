# Proof of Concept: Feature Request: Importing a `js` file could fall back to `ts` file in a `ts` file

**Language:** typescript
**Estimated run time:** < 5 minutes

## Prerequisites

- Node.js 20+, npm install

## How to Run

```bash
npm install
npx ts-node main.ts
```

## What This Demonstrates

Implement a fallback import resolution strategy in Deno for TypeScript files to import '.js' files that may also have '.ts'.
