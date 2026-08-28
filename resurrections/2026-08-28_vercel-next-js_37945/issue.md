# ISR fails to serve 404 pages once the page gets deleted if experimental isr memory cache size is set to 0

**Repository:** [vercel/next.js](https://github.com/vercel/next.js)
**Issue:** [vercel/next.js#37945](https://github.com/vercel/next.js/issues/37945)
**Reactions:** 27 👍
**Created:** 2022-06-23T12:23:35Z
**Last Activity:** 2026-01-16T00:06:40Z
**Labels:** bug, locked, stale

---

## Original Description

### Verify canary release

- [X] I verified that the issue exists in the latest Next.js canary release

### Provide environment information

Operating System:
      Platform: linux
      Arch: x64
      Version: #1 SMP Thu, 16 Jun 2022 13:32:35 +0000
    Binaries:
      Node: 16.15.0
      npm: 8.5.5
      Yarn: 1.22.18
      pnpm: N/A
    Relevant packages:
      next: 12.1.7-canary.45
      react: 18.2.0
      react-dom: 18.2.0


### What browser are you using? (if relevant)

_No response_

### How are you deploying your application? (if relevant)

next start

### Describe the Bug

Deleted ISR page shows old generated document even though it is already revalidated and should show 404 page.
This usually works as expected, but if you disable ISR memory cache (by setting `isrMemoryCacheSize: 0`) it stops and always return the stale version of the page. 

### Expected Behavior

Deleted ISR page should return 404 page

### Link to reproduction

https://github.com/pekarja5/next-isr-cache

### To Reproduce

1. Build and start the production build of provided repo.
2. Navigate to `http://localhost:3000/detail/1`
3. In `public/detail.json` file, change the enabled parameter to 0
4. After 5 seconds (revalidation period) refresh the page twice. First refresh should serve you the stale page while revalidating the page on server and the second should return 404 page, but it does not. Any later request will still serve the original stale version of the page never reaching the expected 404 page. 

---

*Resurrected by Resurrection Bot 🧬*
