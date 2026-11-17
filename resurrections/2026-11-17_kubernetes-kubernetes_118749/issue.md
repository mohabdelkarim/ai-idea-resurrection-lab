# topologySpreadConstraint spanning multiple namespaces

**Repository:** [kubernetes/kubernetes](https://github.com/kubernetes/kubernetes)
**Issue:** [kubernetes/kubernetes#118749](https://github.com/kubernetes/kubernetes/issues/118749)
**Reactions:** 32 👍
**Created:** 2023-06-20T03:17:50Z
**Last Activity:** 2025-07-30T14:15:16Z
**Labels:** sig/scheduling, kind/feature, lifecycle/rotten, needs-triage

---

## Original Description

### What would you like to be added?

I desperately need a way to spread similar prods from different namespaces evenly across clusters nodes.

Right now official docummentation for topologySpreadConstraints explicitly states this:
> Only the Pods holding the same namespace as the incoming Pod can be matching candidates.

I also taken into consideration cluster-wide topologySpreadConstraints, but they seems not covering my case as well, as pods should belong to the same controlling entity (Deployment, Statefulset, Service).

### Why is this needed?

I'm responsible for big enough cluster with hundreds instances of cloud native application that consists of 20+ microservices. Since application may spin up worker pods for data processing pod names are clashing quite often, that's why I have to use namespaces, easy garbage collecting upon removal is another reason.

Application is quite big, so we use resource overprovisioning quite heavily, however, when some nodes getting too many instances of a few specific microservice, it can be easily overloaded. Having global (as opposed to namespaced) topologySpreadConstraints would allow us to optimize capacity requirements a lot.

I'm happy to provide any additional information upon request. Also, any workaround for my use-case is extremely welcome.

Thanks!

---

*Resurrected by Resurrection Bot 🧬*
