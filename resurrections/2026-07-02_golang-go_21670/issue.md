# proposal: Go 2: Have functions auto-implement interfaces with only a single method of that same signature

**Repository:** [golang/go](https://github.com/golang/go)
**Issue:** [golang/go#21670](https://github.com/golang/go/issues/21670)
**Reactions:** 115 👍
**Created:** 2017-08-28T19:43:22Z
**Last Activity:** 2024-08-22T00:54:24Z
**Labels:** LanguageChange, v2, Proposal, NeedsDecision, FrozenDueToAge

---

## Original Description

For example, instead of having to have [http.HandlerFunc](https://golang.org/pkg/net/http/#HandlerFunc), a function with the signature `func(http.ResponsWriter, *http.Request)` would automatically implement [http.Handler](https://golang.org/pkg/net/http/#Handler).

-----

Where I work we have at least 4 internal packages which use some form of interface layering/middleware, similar to `http.Handler` and it's middlewares like [http.StripPrefix](https://golang.org/pkg/net/http/#StripPrefix) and [http.TimeoutHandler](https://golang.org/pkg/net/http/#TimeoutHandler). It's a very powerful pattern which I don't think needs justification (I could give one, but it's not really what this proposal is about).

Having now written a few versions of what's essentially the exact same type I have a few different reasons I think this change is warranted:

* It reduces confusion for programmers new to go. Anecdotally, pretty much every new go developer I've worked with has tried to pass a function like this and been confused as to why they can't. While I understand that this is a fairly small blip on the go learning-curve, I do think this is an indication that this function-as-interface behavior fits better with devs' mental model of how interfaces work.

* It would allow for removing some public-facing types/functions from packages like http (if such a thing is on the table, at the very least it allows for reducing api surface area in new and internal packages). By the same token it reduces code-clutter in cases where something like `HandlerFunc` isn't available and you have to wrap your function in the `WhateverFunc` type inline.

* It would be almost completely backwards compatible. There's no new syntax, and all existing code using types like `http.HandlerFunc` would continue to work as they are. The only exception I can think of is if someone is doing something with a `switch v.(type) {...}`, where `v` _might_ be a function, and the dev expects that the function _won't_ implement the interface as part of that switch behaving correctly (or the equivalent with if-statements or whatever).

These reasons don't justify a language change individually, but in sum I think it becomes worth talking about. Sorry if this has been proposed already, I searched for it but wasn't able to find anything related.

---

*Resurrected by Resurrection Bot 🧬*
