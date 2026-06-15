# Consider making Timeout option required or have a default

**Repository:** [psf/requests](https://github.com/psf/requests)
**Issue:** [psf/requests#3070](https://github.com/psf/requests/issues/3070)
**Reactions:** 66 👍
**Created:** 2016-03-29T16:56:50Z
**Last Activity:** 2024-05-21T10:16:30Z
**Labels:** Feature Request, Breaking API Change

---

## Original Description

I have a feeling I'm about to get a swift education on this topic, but I've been thinking about the pros/cons of changing `requests` so that somehow there is a timeout value configured for every request.

I think there are two ways to do this:
1. Provide a default value. I know browsers have a default, so that may be a simple place to begin.
2. Make every user configure this in every request -- bigger API breakage. Probably not the way to go.

The reason I'm thinking about this is because I've used requests for a few years now and until now I didn't realize the importance of providing a timeout. It took one of my programs hanging forever for me to realize that the default here isn't really very good for my purposes. (I'm in the process of updating all my code...)

I also see that a lot of people want `Session` objects to have a timeout parameter, and this might be a way to do that as well. 

If a large default were provided to all requests and all sessions, what negative impact would that have? The only thing I can think of is that some programs will get timeout exceptions where they previously hung, which seems like an improvement to me.
## Caveat, added May 13, 2016:

Please don't use this issue to discuss adding a timeout attribute to requests. There are a number of discussions about this elsewhere (search closed issues), and we don't want that conversation to muddy this issue too. Thanks.


---

*Resurrected by Resurrection Bot 🧬*
