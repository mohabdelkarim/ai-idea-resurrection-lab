# Better support for sidecar containers in batch jobs

**Repository:** [kubernetes/kubernetes](https://github.com/kubernetes/kubernetes)
**Issue:** [kubernetes/kubernetes#25908](https://github.com/kubernetes/kubernetes/issues/25908)
**Reactions:** 422 👍
**Created:** 2016-05-19T20:55:20Z
**Last Activity:** 2024-11-30T10:56:48Z
**Labels:** area/batch, sig/node, kind/feature, sig/apps, area/workload-api/job, priority/important-longterm, lifecycle/frozen

---

## Original Description

Consider a Job with two containers in it -- one which does the work and then terminates, and another which isn't designed to ever explicitly exit but provides some sort of supporting functionality like log or metric collection.

What options exist for doing something like this? What options should exist?

Currently the Job will keep running as long as the second container keeps running, which means that the user has to modify the second container in some way to detect when the first one is done so that it can cleanly exit as well.

This [question was asked on Stack Overflow](http://stackoverflow.com/questions/36208211/sidecar-containers-in-kubernetes-jobs) a while ago with no better answer than to modify the second container to be more Kubernetes-aware, which isn't ideal. Another customer has recently brought this up to me as a pain point for them.

@kubernetes/goog-control-plane @erictune 


---

*Resurrected by Resurrection Bot 🧬*
