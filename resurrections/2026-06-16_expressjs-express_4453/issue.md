# Allow specifying JSON stringifier

**Repository:** [expressjs/express](https://github.com/expressjs/express)
**Issue:** [expressjs/express#4453](https://github.com/expressjs/express/issues/4453)
**Reactions:** 28 👍
**Created:** 2020-11-02T23:01:37Z
**Last Activity:** 2025-12-03T18:19:43Z
**Labels:** discuss, enhancement

---

## Original Description

It would be great to be able to override the [`JSON.stringify`](https://github.com/expressjs/express/blob/508936853a6e311099c9985d4c11a4b1b8f6af07/lib/response.js#L1122-L1123) call in `res.json()`, to use `json-bigint` to serialize JSON objects

---

*Resurrected by Resurrection Bot 🧬*
