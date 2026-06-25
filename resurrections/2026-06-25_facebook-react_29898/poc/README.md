# Proof of Concept: [React 19] Disabling prerendering siblings of suspended components breaking common pattern

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

The React 19 change breaks a common data fetching pattern, causing performance issues.
