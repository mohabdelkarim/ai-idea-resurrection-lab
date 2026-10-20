# Replace "master" and "slave" terms in Redis

**Repository:** [redis/redis](https://github.com/redis/redis)
**Issue:** [redis/redis#3185](https://github.com/redis/redis/issues/3185)
**Reactions:** 56 👍
**Created:** 2016-04-21T14:19:48Z
**Last Activity:** 2020-08-19T15:06:01Z
**Labels:** 

---

## Original Description

Inspired by django/django/pull/2692, Redis should replace its "master" and "slave" terminology. 

The summary is: `master` and `slave` have racial meanings (especially in North America, but also more generally) and it would be good to avoid them. Django went for `primary` and `replica`. I am not sure what makes the most sense for Redis.

Worth noting, [CouchDB made a similar change](https://issues.apache.org/jira/browse/COUCHDB-2248). [As did Drupal](https://www.drupal.org/node/2275877).


---

*Resurrected by Resurrection Bot 🧬*
