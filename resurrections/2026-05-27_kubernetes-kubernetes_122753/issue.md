# DaemonSet dynamic/scaled resources based on node type

**Repository:** [kubernetes/kubernetes](https://github.com/kubernetes/kubernetes)
**Issue:** [kubernetes/kubernetes#122753](https://github.com/kubernetes/kubernetes/issues/122753)
**Reactions:** 62 👍
**Created:** 2024-01-13T00:45:26Z
**Last Activity:** 2026-05-07T22:42:52Z
**Labels:** kind/feature, sig/apps, lifecycle/rotten, needs-triage

---

## Original Description

### What would you like to be added?

_Intro note: I've read about KEP, however, I'm merely a busy engineer that loves Kubernetes. I'm not sure I can lead my feature request through the KEP process. Please consider this as my initial reach out, if anything to have my voice heard and poll my idea to the community. If there is enough traction, I could follow up and/or someone else could lead it._

I want to propose an enhancement to the DaemonSet (DS) resource management in Kubernetes. The DaemonSet, as it stands, is an invaluable feature for ensuring that each node in a cluster runs a copy of a specific pod. However, I have identified an area where its functionality could be significantly improved: dynamic and scaled resource allocation based on node type.

### Current Limitation: Static Resource Definition

Currently, the resource allocation logic for DaemonSets is rather static. When defining resources for a DaemonSet, such as CPU and memory, it operates on an 'all-or-nothing' basis. This approach does not leverage the full potential of diverse node environments.

### Diverse Node Environment in Current Ecosystem

In the present cloud ecosystem, there's an extensive variety of node types available. These range from nodes with as little as 1 virtual CPU to those as large as 488 CPUs offered by services like AWS. This diversity in node capabilities is not currently accounted for in the DaemonSet design.

### Resource Dependence on Node Size and Pod Density

The workload resources for a DaemonSet, particularly memory and CPU, are often dependent on the number of pods running on a node. More importantly, they can also depend on the size or capacity of the node itself. For instance, a node with more CPUs and memory can, and ideally should, handle more intensive workloads.

### Lack of Native Methods for Dynamic Resource Allocation

As of now, Kubernetes does not offer native methods to define resources for a DaemonSet based on the size or capacity of the node. While it is possible to categorize nodes into groups based on size, this solution is cumbersome and static. It requires significant manual intervention and does not adapt dynamically as the cluster evolves.

### Existing Alternatives

I acknowledge that there are existing methods to manage this challenge, such as adding nodes to different node groups and then using affinity rules to place DaemonSets with different resource requirements. However, this approach is quite tedious and complex. It requires significant manual configuration and continuous adjustment, which detracts from usability and efficiency. This method does not truly cater to the dynamic nature of resource demands in a Kubernetes environment.

### Proposal: Dynamic/Scaled Resource Allocation for DaemonSets

I propose the introduction of a feature that allows DaemonSets to dynamically allocate resources based on the type or capacity of the node. This feature would analyze the node's characteristics (such a

---

*Resurrected by Resurrection Bot 🧬*
