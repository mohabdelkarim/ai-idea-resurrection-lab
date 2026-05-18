# Node.js 15+ starts recommending promise based versions by default - Express 5.0 and wrapAsync

**Repository:** [expressjs/express](https://github.com/expressjs/express)
**Issue:** [expressjs/express#4535](https://github.com/expressjs/express/issues/4535)
**Reactions:** 36 👍
**Created:** 2021-02-23T12:31:48Z
**Last Activity:** 2022-02-17T16:01:51Z
**Labels:** future

---

## Original Description

Hi!

As an example Node.js and https://nodejs.org/api/fs.html is starting to recommend promise-based versions foremost. (compare with earlier versions that has the promised based versions last: https://nodejs.org/docs/latest-v14.x/api/fs.html).

Express 5.0 has added automatic handling in routes of async/await routes that will automatically invoke the Express error handler if a an async function throws. There are current workarounds to create a `wrapAsync()` function around routes, but in bigger projects some users miss this and it's also not-so-nice-looking (and confusing for some).

I am merely wondering if Express 5.0 could be released, and current items on https://github.com/expressjs/express/milestone/11 could be moved to a 6.0 release? I am very respectful of the fact that you voluntarily work on this, and these kind of questions are frowned upon. https://github.com/expressjs/express/pull/2237 was created 7 years ago now, so I at least think it should be ok to ask for this without in any way not being grateful of this project already and its release cadence.

I guess what I am saying is that there are some nice things already on the main branch for Express 5.0 that works good with latest versions of Node.js 15, so a release would be amazing.

---

*Resurrected by Resurrection Bot 🧬*
