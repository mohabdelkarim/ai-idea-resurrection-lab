# Nextjs fails to detect ESM modules correctly when using exports in package.json

**Repository:** [vercel/next.js](https://github.com/vercel/next.js)
**Issue:** [vercel/next.js#39375](https://github.com/vercel/next.js/issues/39375)
**Reactions:** 44 👍
**Created:** 2022-08-06T15:57:15Z
**Last Activity:** 2025-11-05T00:06:30Z
**Labels:** bug, Webpack, linear: next, locked, stale

---

## Original Description

### Verify canary release

- [X] I verified that the issue exists in the latest Next.js canary release

### Provide environment information

    Operating System:
      Platform: darwin
      Arch: arm64
      Version: Darwin Kernel Version 21.2.0: Sun Nov 28 20:28:41 PST 2021; root:xnu-8019.61.5~1/RELEASE_ARM64_T6000
    Binaries:
      Node: 16.16.0
      npm: 8.11.0
      Yarn: 1.22.15
      pnpm: 7.5.2
    Relevant packages:
      next: 12.2.4
      eslint-config-next: 12.2.4
      react: 18.2.0
      react-dom: 18.2.0

### What browser are you using? (if relevant)

_No response_

### How are you deploying your application? (if relevant)

_No response_

### Describe the Bug

Next.js fails to resolve sub dependencies correctly and tries to load CJS from ESM modules, causing the build to fail.

```
SyntaxError: Named export 'theme' not found. The requested module '@chakra-ui/react' is a CommonJS module, which may not support all module.exports as named exports.
CommonJS modules can always be imported via the default export, for example using:
```

@chakra-ui/react a dependency of @saas-ui/react

Saas UI uses exports definition in package.json to define package entries and exports the ESM module as default.

```
{
  "exports": {
    ".": {
      "require": "./dist/index.js",
      "default": "./dist/index.modern.mjs"
    },
    "./src": {
      "default": "./src/index.ts"
    }
  },
  "main": "./dist/index.js",
  "module": "./dist/index.modern.mjs",
  "types": "./dist/index.d.ts"
}
```

Removing exports or changing default to `import` fixes the issue.

However I think Next.js should handle this correctly.



### Expected Behavior

Next.js resolves all packages correctly as ESM.

### Link to reproduction

https://github.com/msnegurski/test-saas-ui

### To Reproduce

1. Clone the repo.
2. npm i
3. npm run dev

Make sure @saas-ui/react@1.2.x is installed (not 1.3)



<sub>[NEXT-1381](https://linear.app/vercel/issue/NEXT-1381/nextjs-fails-to-detect-esm-modules-correctly-when-using-exports-in)</sub>

---

*Resurrected by Resurrection Bot 🧬*
