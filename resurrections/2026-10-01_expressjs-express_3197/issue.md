# express.static - add support for cache-control: immutable

**Repository:** [expressjs/express](https://github.com/expressjs/express)
**Issue:** [expressjs/express#3197](https://github.com/expressjs/express/issues/3197)
**Reactions:** 8 👍
**Created:** 2017-02-03T13:47:13Z
**Last Activity:** 2017-09-28T17:46:31Z
**Labels:** enhancement, module:express-static

---

## Original Description

On static content with versioned URLs, add a flag to options on express.static that generates a cache-control header with immutable, e.g.:
`Cache-Control: max-age=365000000, immutable`
This reduces unnecessary requests in supporting clients.

This is supported by Firefox 49 and used by Facebook:
https://hacks.mozilla.org/2017/01/using-immutable-caching-to-speed-up-the-web/
https://bitsup.blogspot.co.uk/2016/05/cache-control-immutable.html

Supported in Chrome 54
https://bugs.chromium.org/p/chromium/issues/detail?id=611416

Webkit support seems to be added:
https://bugs.webkit.org/show_bug.cgi?id=167497



---

*Resurrected by Resurrection Bot 🧬*
