# Allow to set an expiration on hash field

**Repository:** [redis/redis](https://github.com/redis/redis)
**Issue:** [redis/redis#1042](https://github.com/redis/redis/issues/1042)
**Reactions:** 96 👍
**Created:** 2013-04-08T21:01:14Z
**Last Activity:** 2024-03-31T16:18:05Z
**Labels:** 

---

## Original Description

Right now the `EXPIRE` command only allows to set an expiration time on a key. It would be cool to have the possibility to set it on a field of an hash object. For example:

```
HSET key field "Hello"
EXPIRE key field 10
```

In the example above the `EXPIRE` command sets an expiration time of 10 seconds to the `field` hash field, and not to the `key` object.


---

*Resurrected by Resurrection Bot 🧬*
