# Proof of Concept: .includes or .indexOf does not narrow the type

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

TypeScript does not narrow the type of a union type when using .includes or .indexOf.
