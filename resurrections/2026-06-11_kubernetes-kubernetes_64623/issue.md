# Run job on each node once to help with setup

**Repository:** [kubernetes/kubernetes](https://github.com/kubernetes/kubernetes)
**Issue:** [kubernetes/kubernetes#64623](https://github.com/kubernetes/kubernetes/issues/64623)
**Reactions:** 70 👍
**Created:** 2018-06-01T18:26:45Z
**Last Activity:** 2024-02-18T16:58:17Z
**Labels:** kind/feature, sig/apps, lifecycle/rotten

---

## Original Description

Hello, 

I am looking to see if it is possible to have a job run on each node in the cluster once. Right now our cluster is dynamically provisioned and scaled and was looking to use the kubernetes job and cronjob feature to run things to setup the node once it is provisioned or have a cron make sure something is cleaned up on each node.

---

*Resurrected by Resurrection Bot 🧬*
