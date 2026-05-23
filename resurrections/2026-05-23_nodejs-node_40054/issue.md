# Add utility to synchronously inspect promise state

**Repository:** [nodejs/node](https://github.com/nodejs/node)
**Issue:** [nodejs/node#40054](https://github.com/nodejs/node/issues/40054)
**Reactions:** 32 👍
**Created:** 2021-09-09T15:30:42Z
**Last Activity:** 2024-03-13T06:02:36Z
**Labels:** feature request

---

## Original Description

**Is your feature request related to a problem? Please describe.**

In most cases, you should just await the promise and get its value, even if the promise has already resolved. However, it could sometimes be useful to get the state of the promise. For example, as an optimization to only do a heavy operation if the promise in a certain state or for assertions when writing tests.

**Describe the solution you'd like**

There used to be `process.binding('util').getPromiseDetails(promise)`, but it was removed in Node.js 16. I suggest exposing a `util.promiseState(promise)` method which would return `'pending' | 'fulfilled' | 'rejected'` depending on the promise state.

**Describe alternatives you've considered**

I have made a [package](https://github.com/sindresorhus/p-state) for this, but it depends on parsing `util.inspect()` output which is a bit fragile.


---

*Resurrected by Resurrection Bot 🧬*
