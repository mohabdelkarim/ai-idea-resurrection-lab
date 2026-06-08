# Document threading contract for Session class

**Repository:** [psf/requests](https://github.com/psf/requests)
**Issue:** [psf/requests#2766](https://github.com/psf/requests/issues/2766)
**Reactions:** 77 👍
**Created:** 2015-09-10T13:44:25Z
**Last Activity:** 2025-11-07T00:04:58Z
**Labels:** Documentation

---

## Original Description

Right now, it's quite difficult to figure out if the Session class is threadsafe or not. The docs don't say, apart from a "thread-safe" bullet on the home page. Google led me to http://stackoverflow.com/questions/18188044/is-the-session-object-from-pythons-requests-library-thread-safe, whose first answer boils down to "be very careful".

Inspired by that SO author, I've been auditing the code myself, and have come to the conclusion that Session is probably not threadsafe. (The use of `self.redirect_cache` set off red flags for me.) Reading through other requests bug reports, I see maintainers recommending one Session per thread, which implies that it's not threadsafe.

The documentation should clarify this and recommend how to use Session in multithreaded programs. Possible text:

```
Session is not threadsafe. If you are using requests with an explicit Session
object in a multithreaded program, you should create one Session per thread.
```

If that's accurate, let me know and I'll submit a PR.

Also, I think the "thread-safe" bullet should be removed from the home page, or maybe replaced by "thread-safe in certain circumstances".


---

*Resurrected by Resurrection Bot 🧬*
