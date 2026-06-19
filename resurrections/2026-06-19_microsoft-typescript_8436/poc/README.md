# Proof of Concept: umd module compiler option doesn't have a fallback for global namespace.

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

TypeScript's UMD module compiler option lacks a fallback for the global namespace, causing issues for library developers.
