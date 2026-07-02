# Feature Request: XTRIM option that deletes all messages already acknowledged by all groups

**Repository:** [redis/redis](https://github.com/redis/redis)
**Issue:** [redis/redis#5774](https://github.com/redis/redis/issues/5774)
**Reactions:** 61 👍
**Created:** 2019-01-12T16:47:08Z
**Last Activity:** 2025-07-04T11:02:43Z
**Labels:** class:feature

---

## Original Description

I've been trying to figure out an effective way of trimming streams so that they don't grow unbounded, while taking care to only delete messages that have been acknowledged by all consumer groups. I wound up writing a Lua script to handle it (see https://gist.github.com/chanks/c2e7e0efbd3d038775208047abb68524), but I worry about its efficiency, and think that a built-in option to XTRIM could do this more effectively.

Here's a bit of discussion on the redis-db google group: https://groups.google.com/forum/#!topic/redis-db/99HusgMM7QU

In the meantime, if anyone else needs the above Lua script or has any suggestions on how it could be improved, let me know!

---

*Resurrected by Resurrection Bot 🧬*
