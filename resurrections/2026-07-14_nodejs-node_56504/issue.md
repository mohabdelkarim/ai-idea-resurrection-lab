# A workflow to periodically check status for author-ready PRs opened by a non-collaborator

**Repository:** [nodejs/node](https://github.com/nodejs/node)
**Issue:** [nodejs/node#56504](https://github.com/nodejs/node/issues/56504)
**Reactions:** 22 👍
**Created:** 2025-01-07T15:49:25Z
**Last Activity:** 2026-05-24T01:47:16Z
**Labels:** meta, stale

---

## Original Description

It's quite common for PRs from non-collaborators that have gotten approval to fall through the cracks because there's no one who remember to shepherd it through. I sometimes bump into one of these, and would restart a CI when I see one, but it's very hard to remember to go back keep resuming the CI (sigh) until it's green and land it. And from time to time I also see PRs waiting for months without moving forward due to this reason (not all new contributors know that they have to specifically ping for actions to move it forward, and they could be waiting in vain). I suspect many of the open PRs are stalled this way.

It would help the situation if there is a workflow that gets trigered by the author-ready label and would periodically (e.g. weekly) ping for status if it's opened by a non-collaborator (it's more likely that they don't know how to move it forward), at least sending a notification to the collaborators involved in that PR to press whatever button needed to move it forward.

---

*Resurrected by Resurrection Bot 🧬*
