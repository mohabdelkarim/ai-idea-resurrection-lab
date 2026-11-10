# proposal: must: Do

**Repository:** [golang/go](https://github.com/golang/go)
**Issue:** [golang/go#54297](https://github.com/golang/go/issues/54297)
**Reactions:** 87 👍
**Created:** 2022-08-05T16:14:44Z
**Last Activity:** 2026-06-25T16:14:10Z
**Labels:** Proposal

---

## Original Description

I always find it tedious to use `httputil.ReverseProxy` because you usually need a `*url.URL` and you can't make one easily without a few lines of boilerplate.

Proposal: add `url.MustParse` like regexp.MustCompile, template.Must, etc.

(Alternatively: a generic `must.Do` somewhere in std)

cc @neild 

---

*Resurrected by Resurrection Bot 🧬*
