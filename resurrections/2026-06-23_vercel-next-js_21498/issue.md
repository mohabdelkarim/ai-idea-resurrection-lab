# URL resolution case sensitivity is inconsistent

**Repository:** [vercel/next.js](https://github.com/vercel/next.js)
**Issue:** [vercel/next.js#21498](https://github.com/vercel/next.js/issues/21498)
**Reactions:** 54 👍
**Created:** 2021-01-24T22:00:35Z
**Last Activity:** 2025-10-16T00:05:16Z
**Labels:** bug, locked, stale

---

## Original Description

**What version of Next.js are you using?**

10.0.5

**What version of Node.js are you using?**

14.15.0

**What browser are you using?**

Chrome

**What operating system are you using?**

Windows

**How are you deploying your application?**

Local

**Describe the Bug**

*File system routes*

http://localhost:3000/about -> renders pages/about.js
http://localhost:3000/ABOUT -> 404 not found

Result: case sensitive.

*Redirects*

Using this example: https://github.com/vercel/next.js/tree/canary/examples/redirects

http://localhost:3000/team -> redirects to /about -> renders pages/about.js
http://localhost:3000/TEAM -> redirects to /about -> renders pages/about.js

Result: case insensitive.

*Rewrite*

Using this example: https://github.com/vercel/next.js/tree/canary/examples/rewrites

http://localhost:3000/team -> rewrites to /about -> renders pages/about.js
http://localhost:3000/TEAM -> rewrites to /about -> renders pages/about.js

Result: case insensitive.

**Expected Behavior**

All URL resolution should have a consistent default behavior

*Proposal:*

1) Resolving should be case insensitive, but, if the wrong case is used, a 301 redirect should send the request to the URL with the right case.
2) Same behavior for UTF-8 characters (e.g. https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/String/toLocaleLowerCase to compare UTF-8 characters dependency on https://github.com/vercel/next.js/issues/10084)

Benefits:

- Can be good for people who "type" URLs with the wrong case (e.g. URLs shared using traditional media ads)
- SEO friendly (no duplicate content found on the same case insensitive URL - Google indexes URL case-insensitively)

**To Reproduce**

See description - make sure to open each URL in a new incognito window to avoid Chrome cache hits.



---

*Resurrected by Resurrection Bot 🧬*
