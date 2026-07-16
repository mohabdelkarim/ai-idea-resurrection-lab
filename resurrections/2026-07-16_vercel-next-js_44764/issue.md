# Using generateStaticParams with next/headers causes dynamicParams ignored in production

**Repository:** [vercel/next.js](https://github.com/vercel/next.js)
**Issue:** [vercel/next.js#44764](https://github.com/vercel/next.js/issues/44764)
**Reactions:** 34 👍
**Created:** 2023-01-11T04:44:52Z
**Last Activity:** 2025-09-19T00:05:17Z
**Labels:** bug, linear: next, locked, stale

---

## Original Description

### Verify canary release

- [X] I verified that the issue exists in the latest Next.js canary release

### Provide environment information

    Operating System:
      Platform: linux
      Arch: x64
      Version: #1 SMP PREEMPT_DYNAMIC Sat, 07 Jan 2023 15:10:07 +0000
    Binaries:
      Node: 19.4.0
      npm: 8.19.2
      Yarn: 1.22.19
      pnpm: 7.22.0
    Relevant packages:
      next: 13.1.2-canary.4
      eslint-config-next: 13.1.1
      react: 18.2.0
      react-dom: 18.2.0


### Which area(s) of Next.js are affected? (leave empty if unsure)

App directory (appDir: true)

### Link to the code that reproduces this issue

https://github.com/myl7/next-ignore-dynamic-params-mre

### To Reproduce

The MRE repo contains the code to reproduce the error.

- `pnpm run build && pnpm run start`
- `curl -I http://localhost:3000/posts/1`, returns 200 correctly
- `curl -I http://localhost:3000/posts/2`, return 200 wrongly, expecting 404

### Describe the Bug

When using `generateStaticParams` with `next/headers`, Next.js will return an unexpected error: `Error: Dynamic server usage: headers`. The error can be avoided by disable either `generateStaticParams` or `next/headers` in the development mode. Related https://github.com/vercel/next.js/issues/43427 https://github.com/vercel/next.js/issues/43392 .

But after disabling one of them in development, the app ignore `dynamicParams = false` in the production mode. That means, even using `dynamicParams = false` with `generateStaticParams` to limit available params, the app would still accept dynamic params. In the MRE, even when `slug` of `/posts/[slug]` is limited to `1`, `/posts/2` still returns 200.

### Expected Behavior

`dynamicParams = false` works as expected, which means in the MRE `/posts/2` should return 404.

### Which browser are you using? (if relevant)

Firefox 108.0.2-1 in Arch Linux pacman source

### How are you deploying your application? (if relevant)

Vercel

<sub>[NEXT-1379](https://linear.app/vercel/issue/NEXT-1379/using-generatestaticparams-with-nextheaders-causes-dynamicparams)</sub>

---

*Resurrected by Resurrection Bot 🧬*
