# Proof of Concept: Using generateStaticParams with next/headers causes dynamicParams ignored in production

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

Next.js incorrectly ignores dynamicParams in production when using generateStaticParams with next/headers.
