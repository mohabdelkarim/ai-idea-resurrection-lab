# Proof of Concept: Nextjs fails to detect ESM modules correctly when using exports in package.json

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

Next.js fails to detect ESM modules correctly when using 'exports' in package.json, causing build failures.
