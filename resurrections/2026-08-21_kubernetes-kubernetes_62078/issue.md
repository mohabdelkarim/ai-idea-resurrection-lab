# Feature Request: Create a node's automatic node labels on its pods 

**Repository:** [kubernetes/kubernetes](https://github.com/kubernetes/kubernetes)
**Issue:** [kubernetes/kubernetes#62078](https://github.com/kubernetes/kubernetes/issues/62078)
**Reactions:** 34 👍
**Created:** 2018-04-03T19:33:40Z
**Last Activity:** 2024-10-28T17:17:56Z
**Labels:** sig/scheduling, sig/node, kind/feature, lifecycle/rotten

---

## Original Description

<!-- This form is for bug reports and feature requests ONLY! 

If you're looking for help check [Stack Overflow](https://stackoverflow.com/questions/tagged/kubernetes) and the [troubleshooting guide](https://kubernetes.io/docs/tasks/debug-application-cluster/troubleshooting/).
-->

**Is this a BUG REPORT or FEATURE REQUEST?**:

> Uncomment only one, leave it on its own line: 
>
> /kind bug

/kind feature


**What happened**:
Cannot tell Kafka broker pod which failure domain it is in for rack-awareness.

**What you expected to happen**: 
Pods would inherit these labels from the node:
https://kubernetes.io/docs/concepts/configuration/assign-pod-node/#interlude-built-in-node-labels

**How to reproduce it (as minimally and precisely as possible)**:
N/A

**Anything else we need to know?**:
This approach would be a kind of alternative to these:
- https://github.com/kubernetes/kubernetes/issues/40610
- https://github.com/kubernetes/kubernetes/pull/25957
- https://github.com/Yolean/kubernetes-kafka/pull/41

Also relevant:
- https://github.com/minio/minio/issues/5738

**Environment**:
- Kubernetes version (use `kubectl version`): v1.10.0
- Cloud provider or hardware configuration: AWS
- OS (e.g. from /etc/os-release):
- Kernel (e.g. `uname -a`):
- Install tools: Kops
- Others:


---

*Resurrected by Resurrection Bot 🧬*
