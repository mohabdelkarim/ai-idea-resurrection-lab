# Add Support to Deny RBAC Rules

**Repository:** [kubernetes/kubernetes](https://github.com/kubernetes/kubernetes)
**Issue:** [kubernetes/kubernetes#85963](https://github.com/kubernetes/kubernetes/issues/85963)
**Reactions:** 100 👍
**Created:** 2019-12-05T19:11:09Z
**Last Activity:** 2024-03-18T15:59:01Z
**Labels:** priority/awaiting-more-evidence, kind/feature, sig/auth

---

## Original Description

(_I am opening this ticket on behalf of the author of https://github.com/kubernetes/community/issues/4061 - because we are also having the same problem and it's problematic for us. The text in this ticket is a direct copy and paste_)

**What would you like to be added**:
Add `Kind: <Allow/Deny>` to the RBAC `Rules` key. Default to `Allow. Example:

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  namespace: ns
  name: role
rules:
  - kind: Allow
    apiGroups:
      - ''
      - apps
      - extensions
    resources:
      - '*'
    verbs:
      - '*'
  - kind: Deny
    apiGroups:
      - ''
    resources:
      - 'secrets'
    verbs:
      - 'get'
      - 'watch'
      - 'list'
```

**Why is this needed**:
The absence of denial rules in K8s makes it difficult or impracticable to restrict access while being permissive.

Some use cases would be:

Allow user to perform all actions that do not involve kube-system namespace. Including being able to create new namespaces and automatically have access granted to perform actions on it.
Prevent secrets from being accessed by some subject in a namespace and have access to custom resources without having to list all of them manually.


---

*Resurrected by Resurrection Bot 🧬*
