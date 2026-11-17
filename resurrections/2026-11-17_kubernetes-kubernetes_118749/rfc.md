# RFC: topologySpreadConstraint spanning multiple namespaces

Summary
The Kubernetes scheduler will gain a new plugin, **CrossNamespaceSpread**, that enables TopologySpreadConstraints (TSC) to consider Pods from *any* namespace when evaluating the maxSkew rule.  An optional boolean `crossNamespace` flag on each TSC entry activates this behavior.  The plugin is gated behind the `CrossNamespaceSpread` feature gate, allowing incremental adoption and rollback.  The change leverages the scheduler framework introduced in v1.28, the CrossNamespaceSpread feature gate added in v1.29, and the updated API types generated in client-go v0.30.

Motivation
Current TSC semantics only count Pods that share the same namespace as the incoming Pod.  This limitation prevents cluster operators from achieving true multi‑tenant load balancing across zones, racks, or other topology domains when workloads are split across namespaces for security or organizational reasons.  As clusters grow to thousands of nodes and dozens of namespaces, uneven pod placement can cause hot spots, increase latency, and waste resources.  Providing a cross‑namespace spread option solves a real‑world need for multi‑tenant clusters, aligns with the broader goal of “cluster‑wide fairness,” and does not require users to merge unrelated workloads into a single namespace.

Detailed Design
1. **API Extension** – Add a new optional field to `v1.TopologySpreadConstraint`:
   ```go
   // +optional
   // CrossNamespace indicates that the constraint should consider Pods from all namespaces.
   // When false (default), the existing same‑namespace behavior is retained.
   CrossNamespace bool `json:"crossNamespace,omitempty"`
   ```
   The field is versioned in `v1` and reflected in the generated client‑go types.

2. **Feature Gate** – Register `CrossNamespaceSpread` (default off) in `pkg/features/features.go`.  The scheduler will refuse to load the plugin if the gate is disabled.

3. **Scheduler Plugin** – Implement `CrossNamespaceSpread` as a `framework.ScorePlugin` and `framework.PreFilterPlugin`.
   * **PreFilter** – For each constraint with `crossNamespace=true`, build a selector from `LabelSelector` and store it in the cycle state.
   * **Score** – Query the shared informer cache (`podInformer`) for *all* Pods, filter by the selector, and count matching Pods per node keyed by `topologyKey`.  Compute the score as `maxSkew - count` (clamped to 0) and add it to the node’s total score.  The plugin respects `maxSkew`, `whenUnsatisfiable`, and `topologyKey` exactly as the built‑in TSC plugin.
   * **Concurrency** – The plugin reads from the read‑only informer cache; no locking is required.

4. **Registration** – In `cmd/kube-scheduler/app/options.go`, add the plugin to the default profile when the feature gate is on.  The plugin name is `CrossNamespaceSpread` and it is placed after the existing `NodeAffinity` plugin.

5. **Testing** – Add unit tests using the scheduler‑framework test harness:
   * Verify that with `crossNamespace=false` behavior matches the legacy plugin.
   * Verify that with `crossNamespace=true` pods from other namespaces are counted.
   * Validate scoring respects `maxSkew` and produces deterministic node ordering.
   Integration tests will run against a real control‑plane (kind) cluster with the feature gate enabled.

6. **Documentation** – Update the API reference, the scheduling guide, and the feature‑gate documentation to describe the new flag, its semantics, and recommended usage patterns.

Drawbacks
* **Increased Cache Load** – The plugin queries the informer cache for all Pods, which can increase memory pressure on large clusters.  Mitigation: the plugin reuses the existing pod list cache and applies efficient label selectors; additional metrics will be added to monitor cache hit rates.
* **Potential Inter‑Namespace Interference** – Enabling cross‑namespace spreading may unintentionally cause one tenant’s workload to affect another’s placement, which could be undesirable in strict multi‑tenant environments.  Operators must enable the flag only on constraints where such coupling is acceptable.
* **Complexity in Debugging** – Scheduler logs will now include cross‑namespace counts, adding noise for users unfamiliar with the feature.  The plugin will emit a concise log level (`V=4`) entry per scheduling cycle.

Alternatives
1. **Controller‑Based Rebalancing** – Write a separate controller that periodically evicts Pods to achieve cross‑namespace balance.  This approach is reactive, incurs additional churn, and cannot guarantee optimal placement at pod creation time.
2. **Namespace‑Level Aggregation** – Introduce a new top‑level resource (e.g., `SpreadPolicy`) that aggregates constraints across namespaces.  This would require a larger API surface and new admission checks, increasing implementation effort.
3. **Extend Existing TSC Plugin** – Modify the built‑in TSC plugin to add a global flag.  This would couple cross‑namespace logic with same‑namespace logic, making the code harder to maintain and preventing independent feature‑gate control.
   The plugin approach offers the cleanest separation, leverages the scheduler framework, and provides granular per‑constraint control.

Unresolved Questions
* **Cache Eviction Policy** – How should the plugin react when the pod informer cache is stale or truncated?  Should it fallback to a live API call for missing Pods, or simply ignore them?
* **Metric Exposure** – What specific Prometheus metrics should be added to observe cross‑namespace spread effectiveness (e.g., `scheduler_cross_namespace_spread_total`)?
* **Security Implications** – Does counting Pods across namespaces expose any information that could be abused for inference attacks?  A review with the security team is needed.
* **Interaction with PodDisruptionBudgets** – Will cross‑namespace spreading interfere with PDB calculations when evictions occur?  Preliminary tests show no conflict, but formal verification is pending.

---

*RFC generated by Resurrection Bot 🧬*
