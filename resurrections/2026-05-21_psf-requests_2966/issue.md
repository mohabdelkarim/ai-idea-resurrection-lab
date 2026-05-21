# Consider using system trust stores by default in 3.0.0.

**Repository:** [psf/requests](https://github.com/psf/requests)
**Issue:** [psf/requests#2966](https://github.com/psf/requests/issues/2966)
**Reactions:** 92 👍
**Created:** 2016-01-11T17:15:47Z
**Last Activity:** 2025-05-20T00:05:04Z
**Labels:** Please Review, Question/Not a bug, Needs More Information

---

## Original Description

It's been raised repeatedly, mostly by people using Linux systems, that it's annoying that requests doesn't use the system trust store and instead uses the one that certifi ships. This is an understandable position. I have some personal attachment to the certifi approach, but the other side of that argument definitely has a reasonable position too. For this reason, I'd like us to look into whether we should use the system trust store by default, and make certifi's bundle a fallback option.

I have some caveats here:
1. If we move to the system trust store, we must do so on _all_ platforms: Linux must not be its own special snowflake.
2. We must have broad-based support for Linux and Windows.
3. We must be able to fall back to certifi cleanly.

Right now it seems like the best route to achieving this would be to use [certitude](https://github.com/python-hyper/certitude). This currently has support for dynamically generating the cert bundle OpenSSL needs directly from the system keychain on OS X. If we added Linux and Windows support to that library, we may have the opportunity to switch to using certitude.

Given @kennethreitz's bundling policy, we probably cannot unconditionally switch to certitude, because certitude depends on cryptography (at least on OS X). However, certitude could take the current privileged position that certifi takes, or be a higher priority than certifi, as an optional dependency that is used if present on the system.

Thoughts? This is currently a RFC, so please comment if you have opinions. /cc @sigmavirus24 @alex @kennethreitz @dstufft @glyph @reaperhulk @morganfainberg


---

*Resurrected by Resurrection Bot 🧬*
