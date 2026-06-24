# Finding by owner username/group/uid/gid

**Repository:** [sharkdp/fd](https://github.com/sharkdp/fd)
**Issue:** [sharkdp/fd#307](https://github.com/sharkdp/fd/issues/307)
**Reactions:** 20 👍
**Created:** 2018-06-27T21:01:58Z
**Last Activity:** 2020-05-19T17:02:36Z
**Labels:** help wanted, feature-request

---

## Original Description

Hello,

I've been using `fd` for quite a long time, and loving it! Recently I've found myself needing to search for files owned by one user or another. I'm willing to do any implementation work required for it, and i'd like to start off a discussion and see if anyone else here has had a need for this feature.

Interface-wise, my first proposal would be to add a `--user` (as well as a `--group` switch) in the style of find, and maybe they could handle a uid/gid by default when passed a number.

Another idea, which is more flexible and less backwards-looking would be passing an `--owner` flag that can parse a `[(uid|username)][:(gid|groupname)]` input pair. As a precedent, docker's `--user` does this. Maybe it would make sense to call the flag `--user` in fd also, but i'm personally worried that it would make finding the "search by gid" option a little more obscure or unintuitive.

Lastly, I really don't know what to say right now about negative reasoning. I haven't encountered the need per se, but it feels "natural" in a way to be able to search for files "not owned by my user in this directory". Any ideas of how (or if) to do negation/exclusion by owner are welcome.

I'll start to hack a prototype together, and I'm really curious as what people think about this option.

---

*Resurrected by Resurrection Bot 🧬*
