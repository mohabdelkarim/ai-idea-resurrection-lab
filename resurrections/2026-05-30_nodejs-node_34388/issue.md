# Add experimental support for io_uring

**Repository:** [nodejs/node](https://github.com/nodejs/node)
**Issue:** [nodejs/node#34388](https://github.com/nodejs/node/issues/34388)
**Reactions:** 54 👍
**Created:** 2020-07-16T03:04:21Z
**Last Activity:** 2023-11-20T21:59:25Z
**Labels:** discuss, feature request, libuv, performance, linux, stale, never-stale

---

## Original Description

<!--
Thank you for suggesting an idea to make Node.js better.

Please fill in as much of the template below as you're able.
-->

Recent Linux kernel (5.1+) includes io_uring, a new non-blocking I/O subsystem, which might serve as a more efficient alternative to epoll. We could benefit from it and get a performance improvement in network I/O scenarios with high volume of concurrent connections and/or for fs operations.

Of course, in Node.js case we need changes made in libuv. There is an ongoing experiment aimed to add support for io_uring in libuv: https://github.com/libuv/libuv/pull/2322

As this feature should be experimental (at least initially), io_uring mode could be activated under a new flag.

The goal of this issue is to improve visibility of the libuv experiment and gather some feedback.

---

*Resurrected by Resurrection Bot 🧬*
