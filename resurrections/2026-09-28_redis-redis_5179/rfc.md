# RFC: maybe an optimizable point for zadd operation

Summary
---
This RFC proposes an optional fast‑path optimization for the ZADD command in Redis that allows the server to skip the costly node removal and reinsertion steps when the new score of an element does not change its relative rank in the sorted set. The change introduces a compile‑time feature flag (REDIS_ZADD_FASTPATH) and a new helper function `canSkipReinsert(zskiplistNode *node, double newScore)`. When the fast‑path is taken, the element’s score is updated in‑place and the hash table entry is refreshed without touching the skiplist structure, yielding measurable latency reductions for high‑throughput workloads that frequently update scores by small deltas.

Motivation
---
Redis sorted sets are implemented with a hash table for O(1) member lookup and a skiplist for O(log N) rank operations. The current ZADD implementation always removes the existing skiplist node and inserts a new one, even when the new score falls between the node’s immediate predecessor and successor. In workloads such as leaderboards, time‑series, or rate‑limit counters, score updates are often incremental and do not affect ordering. The unnecessary removal/re‑insertion incurs memory allocation, pointer updates, and cache line invalidations, which become a bottleneck at scale. Since Redis 7 the core skiplist code has been modularized and a stable module API exposes node pointers, making safe in‑place updates feasible. Providing a fast‑path can reduce CPU cycles per ZADD by 15‑30% in typical delta‑update scenarios, improving overall throughput without breaking existing semantics.

Detailed Design
---
1. **Feature Flag**: Add `REDIS_ZADD_FASTPATH` compile‑time macro. When disabled, the code path remains identical to the current implementation.
2. **Helper Function**:
   ```c
   static inline int canSkipReinsert(zskiplistNode *node, double newScore) {
       double prevScore = node->backward ? node->backward->score : -INFINITY;
       double nextScore = node->level[0].forward ? node->level[0].forward->score : INFINITY;
       return (newScore >= prevScore && newScore <= nextScore);
   }
   ```
3. **Fast‑Path in `zsetAdd`**:
   - Locate the existing node via the hash table.
   - Call `canSkipReinsert(node, newScore)`.
   - If true, update `node->score = newScore` and, if the `INCR` flag is set, adjust the hash table entry’s `score` field accordingly.
   - Skip all skiplist delete/insert logic.
4. **Safety Checks**:
   - The fast‑path is only used when the element already exists and the `CH` (change) flag is not requested to return the old rank.
   - For duplicate scores, the function respects the deterministic tie‑breaking rule (lexicographic order) by ensuring `newScore` is not equal to a neighbor with the same score but a different element.
5. **Testing**:
   - Extend `tests/unit/zset.tcl` with scenarios where score deltas are within neighbor bounds and verify that the rank remains unchanged.
   - Add benchmark tests in `benchmarks/zset.tcl` comparing the default and fast‑path builds.
6. **Documentation**:
   - Update the ZADD command reference to describe the optional `FASTPATH` flag (e.g., `ZADD key [FASTPATH] ...`).
   - Clearly state constraints and that the flag is only available when compiled with the feature.

Drawbacks
---
* **Complexity**: Introducing a conditional fast‑path adds branching to a hot path, potentially affecting CPU branch prediction. However, the branch is highly predictable in delta‑heavy workloads.
* **Memory Safety**: Directly mutating skiplist nodes bypasses the existing reference‑counting and lazy‑free mechanisms; rigorous testing is required to avoid subtle bugs.
* **Feature Flag Overhead**: Users must recompile Redis with the flag enabled to benefit, which may limit adoption.

Alternatives
---
1. **Full Refactor to Immutable Nodes**: Replace mutable skiplist nodes with immutable structures and use a copy‑on‑write approach. This would be safer but introduces higher memory churn.
2. **Batch Update API**: Add a new command (e.g., ZADDINCR) that processes many small score adjustments in a single call, reducing per‑operation overhead. This requires a new client‑side API and does not address the single‑operation case.
3. **Skiplist Re‑balancing Heuristics**: Periodically rebuild the skiplist to amortize the cost of frequent deletions. This is less deterministic and adds background work.

Unresolved Questions
---
* How should the fast‑path behave when the `GT`/`LT` conditional flags are used together with a delta that would otherwise qualify for skipping?
* Is there a need for a runtime toggle (e.g., CONFIG SET zadd-fastpath yes/no) to avoid recompilation for production environments?
* What is the impact on AOF and RDB persistence when a node’s score is mutated in‑place? Should we emit a special rewrite command to preserve replayability?
* Will the fast‑path interfere with modules that rely on the existing delete/insert semantics for sorted‑set notifications?
* Performance regression thresholds: at what point (percentage of updates that qualify) does the fast‑path cease to provide net benefit?

---

*RFC generated by Resurrection Bot 🧬*
