# proposal: leave "if err != nil" alone?

**Repository:** [golang/go](https://github.com/golang/go)
**Issue:** [golang/go#32825](https://github.com/golang/go/issues/32825)
**Reactions:** 2008 👍
**Created:** 2019-06-28T08:42:25Z
**Last Activity:** 2020-12-09T04:16:22Z
**Labels:** Proposal, FrozenDueToAge, Proposal-Hold, error-handling

---

## Original Description

The Go2 proposal #32437 adds new syntax to the language to make the `if err != nil { return ... }` boilerplate less cumbersome.

There are various alternative proposals: #32804 and #32811 as the original one is not universally loved.

To throw another alternative in the mix: **Why not keep it as is**?

I've come to like the explicit nature of the `if err != nil` construct and as such I don't understand why we need new syntax for this. Is it really that bad?

---

*Resurrected by Resurrection Bot 🧬*
