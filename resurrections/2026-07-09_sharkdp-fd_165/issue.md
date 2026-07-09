# Search based on file timestamps (atime, ctime, mtime)

**Repository:** [sharkdp/fd](https://github.com/sharkdp/fd)
**Issue:** [sharkdp/fd#165](https://github.com/sharkdp/fd/issues/165)
**Reactions:** 17 👍
**Created:** 2017-11-11T17:16:30Z
**Last Activity:** 2025-11-10T09:48:29Z
**Labels:** feature-request, good first issue

---

## Original Description

`find` has this very useful feature that I use often, which is timestamp-based file search. You're probably familiar with it already, but here's the documentation for those flags:

```
-atime n
              File  was  last  accessed n*24 hours ago.  When find figures out
              how many 24-hour periods ago the file  was  last  accessed,  any
              fractional part is ignored, so to match -atime +1, a file has to
              have been accessed at least two days ago.

-ctime n
              File's status was last changed n*24 hours ago.  See the comments
              for -atime to understand how rounding affects the interpretation
              of file status change times.

-mtime n
              File's  data was last modified n*24 hours ago.  See the comments
              for -atime to understand how rounding affects the interpretation
              of file modification times.
```

What do you think? Thank you.

---

*Resurrected by Resurrection Bot 🧬*
