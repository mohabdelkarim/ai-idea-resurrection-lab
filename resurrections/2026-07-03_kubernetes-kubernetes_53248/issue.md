# kubectl provides a way to find which RoleBinding/ClusterRoleBinding is related to a serviceAccount

**Repository:** [kubernetes/kubernetes](https://github.com/kubernetes/kubernetes)
**Issue:** [kubernetes/kubernetes#53248](https://github.com/kubernetes/kubernetes/issues/53248)
**Reactions:** 39 👍
**Created:** 2017-09-29T07:13:15Z
**Last Activity:** 2024-04-03T13:57:18Z
**Labels:** area/kubectl, priority/awaiting-more-evidence, kind/feature, sig/cli, lifecycle/frozen

---

## Original Description

<!-- This form is for bug reports and feature requests ONLY! 

If you're looking for help check [Stack Overflow](https://stackoverflow.com/questions/tagged/kubernetes) and the [troubleshooting guide](https://kubernetes.io/docs/tasks/debug-application-cluster/troubleshooting/).
-->

**Is this a BUG REPORT or FEATURE REQUEST?**: 

/kind feature


**What happened**:
When I encounter a problem which is caused by no proper permissions, I want to find which RoleBinding/ClusterRoleBinding is related to the serviceAccount the Pod uses. But there's no simple way to do this without traversing all of the bindings.

**What you expected to happen**:
`kubectl` could provide a simple method to solve the above problem such as:

```shell
$ kubectl get rolebinding SERVICE_ACCOUNT_NAME POD
$ kubectl get clusterrolebinding SERVICE_ACCOUNT_NAME POD
```

**How to reproduce it (as minimally and precisely as possible)**:


**Anything else we need to know?**:

Related stackoverflow problems: [Is there a way to find the RoleBinding/ClusterRoleBinding related to a serviceAccount?](https://stackoverflow.com/questions/46482455/is-there-a-way-to-find-the-rolebinding-clusterrolebinding-related-to-a-serviceac)

**Environment**:
- Kubernetes version (use `kubectl version`):
- Cloud provider or hardware configuration**:
- OS (e.g. from /etc/os-release):
- Kernel (e.g. `uname -a`):
- Install tools:
- Others:


---

*Resurrected by Resurrection Bot 🧬*
