# [React 19] Disabling prerendering siblings of suspended components breaking common pattern

**Repository:** [facebook/react](https://github.com/facebook/react)
**Issue:** [facebook/react#29898](https://github.com/facebook/react/issues/29898)
**Reactions:** 261 👍
**Created:** 2024-06-14T13:19:59Z
**Last Activity:** 2025-06-12T17:43:06Z
**Labels:** React 19

---

## Original Description

## Summary

<!--
  Please provide a CodeSandbox (https://codesandbox.io/s/new), a link to a
  repository on GitHub, or provide a minimal code example that reproduces the
  problem. You may provide a screenshot of the application if you think it is
  relevant to your bug report. Here are some tips for providing a minimal
  example: https://stackoverflow.com/help/mcve.
-->

I'm creating this issue to continue the discussion that spawned in the already merged PR (#26380)

Several community members have raised concerns about this change and it has gained traction on both X and Reddit as well, I think it is important to prioritize this discussion as it can be a dealbreaker whether or not a project will upgrade to React 19 at all of this is not addressed.

### The problem

This change causes sibling components of suspended components to not prerender, meaning that it will cause performance problems when using a very common pattern where you do data fetching near to where the data is actually used. It makes requests that would before be performed in parallel due to prerendering triggering them, into waterfall requests instead. Here's screenshots from @matiasngf and part of their description from [the pull request comment](https://github.com/facebook/react/pull/26380#issuecomment-2166178673):

> First, we recorded the current approach; it takes about 2.5 seconds to load the .glb models:

<img width="479" alt="image" src="https://github.com/facebook/react/assets/586152/b1caa7e0-5938-4ad5-9751-ee248776ab80">

> Then, we installed the canary version of react; Same .glb models, takes about 3.5 seconds to load:

<img width="483" alt="image" src="https://github.com/facebook/react/assets/586152/0e5083f8-fdd3-46d9-92ce-851dc6b4b985">

I included the above example in the issue body because it is a great illustration of the problem. Their comment also include links to both their current site that doesn't have the problem and also a version of their site with an updated React with the problem present.

### Discussions around potential fixes

There are several ways to approach this, but I think @matiasperz were [spot on when suggesting that this entire change be opt-in](https://github.com/facebook/react/pull/26380#issuecomment-2166342228). The changed logic seems like the part that should be opt-in, and the default behavior should be the way things worked before the change.

Something along the lines of:
`strategy={"parallel" | "sequential"}` where it is clear how suspended components will behave.

### Conclusion

While not exactly a breaking change in the literal sense, I would personally consider this a breaking change and worse, one that it is not possible to easily migrate away from without changing the entire data fetching pattern for your application. The other option being just eating the performance loss but no one is realistically going to do that.

Moving data fetching up is not a good recommendation, since it goes ag

---

*Resurrected by Resurrection Bot 🧬*
