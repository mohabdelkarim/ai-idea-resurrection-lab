# maybe an optimizable point for zadd operation

**Repository:** [redis/redis](https://github.com/redis/redis)
**Issue:** [redis/redis#5179](https://github.com/redis/redis/issues/5179)
**Reactions:** 62 👍
**Created:** 2018-07-28T04:56:03Z
**Last Activity:** 2022-06-13T09:06:37Z
**Labels:** 

---

## Original Description

When we use zadd command to update the score for exists value，if the score delta is small，element rank will be no change，i think we only need change the score, while deleting and reinserting is unnecessary.

To be sure the rank is not changed, we can use current node's forward and backward pointer to access the sibling nodes, to test whether the new score is still between the score of prev and next node.

The following source code is clipped from current redis repo.

```c
int zsetAdd(robj *zobj, double score, sds ele, int *flags, double *newscore) {
...
            /* Remove and re-insert when score changes. */
            if (score != curscore) {
                zskiplistNode *node;
                serverAssert(zslDelete(zs->zsl,curscore,ele,&node));
                znode = zslInsert(zs->zsl,score,node->ele);
                /* We reused the node->ele SDS string, free the node now
                 * since zslInsert created a new one. */
                node->ele = NULL;
                zslFreeNode(node);
                /* Note that we did not removed the original element from
                 * the hash table representing the sorted set, so we just
                 * update the score. */
                dictGetVal(de) = &znode->score; /* Update score ptr. */
                *flags |= ZADD_UPDATED;
            }
...
```

---

*Resurrected by Resurrection Bot 🧬*
