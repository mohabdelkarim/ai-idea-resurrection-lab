# Support httpHead for pod livenessProbe

**Repository:** [kubernetes/kubernetes](https://github.com/kubernetes/kubernetes)
**Issue:** [kubernetes/kubernetes#49937](https://github.com/kubernetes/kubernetes/issues/49937)
**Reactions:** 33 👍
**Created:** 2017-08-01T10:45:20Z
**Last Activity:** 2025-06-27T11:29:55Z
**Labels:** sig/node, kind/feature, lifecycle/rotten, needs-triage

---

## Original Description

/kind feature

**What happened**:
The docs for [http liveness probes](https://kubernetes.io/docs/tasks/configure-pod-container/configure-liveness-readiness-probes/#define-a-liveness-http-request) only reference `httpGet`, but a http `HEAD` request is better for healthchecks as no data is returned so it is lighter weight.

**What you expected to happen**:
I would expect a httpHead directive to exist. It would perform a request such as:

```
HEAD / HTTP/1.1
```

vs `httpGet`, which does something like:

```
GET / HTTP/1.1
```

**How to reproduce it (as minimally and precisely as possible)**:

Create a livenessProbe and be :disappointed:  that `HEAD` requests aren't available.

---

*Resurrected by Resurrection Bot 🧬*
