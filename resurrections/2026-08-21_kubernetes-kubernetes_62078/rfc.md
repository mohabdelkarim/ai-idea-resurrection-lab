# RFC: Feature Request: Create a node's automatic node labels on its pods 

Summary
Kubernetes will automatically copy a configurable set of node labels onto every Pod that the scheduler places on that node. The feature is gated by the NodeLabelPropagation feature gate and is opt‑in per‑Pod via an annotation. The propagation is performed by a cluster‑wide Admission webhook that queries a lightweight node‑label cache provided by the scheduler and injects the selected labels into the Pod's metadata before it is persisted. Operators configure the list of propagatable label keys in a ConfigMap, allowing them to expose only safe, non‑sensitive node metadata to workloads.

Motivation
Many workloads need to know the topology or hardware characteristics of the node they run on (e.g., zone, instance‑type, custom rack identifiers) in order to make intra‑application decisions such as affinity, logging, or licensing. Currently, this information must be discovered via the Downward API, environment variables, or by querying the Kubernetes API directly, which requires additional RBAC permissions and adds latency. By automatically copying selected node labels onto the Pod, we provide a zero‑configuration, low‑latency path for workloads to access node metadata while preserving security boundaries through explicit configuration and opt‑in semantics.

Detailed Design
1. Feature Gate: Add `NodeLabelPropagation` to the feature gate registry. Disabled by default.
2. ConfigMap `node-label-propagation-config` in `kube-system` namespace:
   ```yaml
   apiVersion: v1
   kind: ConfigMap
   metadata:
     name: node-label-propagation-config
     namespace: kube-system
   data:
     allowedLabels: "failure-domain.beta.kubernetes.io/zone,instance-type,custom-rack"
   ```
   The `allowedLabels` field is a comma‑separated list of node label keys that may be propagated.
3. Admission Webhook:
   - Deploy as a static pod in the control‑plane (`node-label-propagation-webhook`).
   - Implements the `admission.k8s.io/v1` API, registered for `pods/create` operations.
   - Reads the ConfigMap at startup and watches for updates.
   - For each incoming Pod, checks the annotation `node-label-propagation.kubernetes.io/enable: "true"`. If absent or false, the webhook is a no‑op.
   - Retrieves the node name from `spec.nodeName` (if already set) or, if not yet scheduled, defers to the scheduler cache via a new `SchedulerCache` gRPC service exposing allowed label values per node.
   - Injects the allowed labels as entries under `metadata.labels` with a `node.k8s.io/` prefix to avoid clashes, e.g., `node.k8s.io/zone: us-east1-b`.
4. Scheduler Changes:
   - Extend the scheduler's cache to store a map of allowed label keys per node (populated from the ConfigMap at startup).
   - Expose a lightweight gRPC endpoint `NodeLabelPropagationService` that the webhook can call to retrieve labels for a given node without a full API server round‑trip.
5. Kubelet Changes:
   - Add a read‑only endpoint `/node-labels` (secured via the existing kubelet authentication) that returns the node’s allowed labels in JSON. This is used by the webhook when the pod is already bound.
   - No changes to pod execution; the injected labels are treated like any other pod label.
6. RBAC:
   - The webhook ServiceAccount receives `get` permission on the ConfigMap and `list/watch` on `nodes` (restricted to the `metadata.labels` field).
   - The webhook can optionally use the new kubelet endpoint, guarded by the `system:node-proxier` group.

Drawbacks
- Security: Propagating node labels exposes node metadata to pods. Misconfiguration of `allowedLabels` could leak sensitive information (e.g., internal IP ranges). The opt‑in annotation mitigates accidental exposure but does not protect a malicious user who can add the annotation.
- Performance: Introducing a webhook adds latency to pod creation. The design caches labels and uses a scheduler cache to keep overhead under ~2 ms per request, but high‑throughput clusters may see a measurable impact.
- Operational Complexity: Operators must manage the ConfigMap and monitor the webhook health. Failure of the webhook will block all opted‑in pods, potentially causing scheduling dead‑locks.

Alternatives
1. Use the existing Downward API `nodeLabels` field (introduced in v1.27) – however it requires explicit field specification in each pod manifest and does not support dynamic configuration.
2. Extend the CRI to pass node labels directly to the container runtime – this would require changes across all CRI implementations and does not provide a Kubernetes‑level label view.
3. Implement the propagation entirely inside the scheduler by mutating the Pod object before it is persisted. This would bypass the Admission control layer but would break the separation of concerns and make rollback harder.

Unresolved Questions
- What granularity of label prefix should be enforced to avoid collisions with user‑defined labels?
- How should the feature behave for Pods that are created without a specified node (i.e., pending) and later bound? Should the webhook re‑invoke on binding events?
- Should there be a mechanism to whitelist namespaces for automatic propagation, or rely solely on the per‑Pod annotation?
- How will the feature interact with PodSecurityPolicies or the newer Pod Security Standards that may restrict label modifications?
- What monitoring and alerting metrics are needed to detect latency spikes or webhook failures?

---

*RFC generated by Resurrection Bot 🧬*
