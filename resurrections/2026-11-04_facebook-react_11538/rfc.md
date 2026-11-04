# RFC: Make React resilient to DOM mutations from Google Translate

1. Summary
React currently assumes exclusive ownership of the DOM subtree it renders. When Google Translate rewrites elements (e.g., inserting <span> wrappers or changing text nodes), React's commit phase can encounter unexpected nodes, leading to thrown errors or corrupted UI. This RFC proposes adding a resilient root wrapper that detects external DOM mutations via MutationObserver, defers unsafe DOM operations, and integrates with the new concurrent rendering pipeline to keep the virtual DOM and real DOM in sync without breaking existing contracts.

2. Motivation
Google Translate is widely used on public-facing sites, and many React applications are deployed in multilingual contexts. The lack of handling for external DOM mutations manifests as "Invariant Violation" errors during hydration or updates, degrading user experience and increasing support tickets. React 16 lacked a hook to observe external changes; React 18’s concurrent scheduler and the availability of MutationObserver now make it feasible to add a safety net. Providing built‑in resilience will:
- Reduce crashes on sites that enable automatic translation.
- Lower the maintenance burden for developers who currently need work‑arounds (e.g., disabling translate or manually cleaning the DOM).
- Strengthen React’s promise of being a predictable UI library even in hostile environments.

3. Detailed Design
a. RootWrapper Component
   - Export a new API `createRootWithSafety(container, options)` that returns a root object identical to `createRoot` but internally attaches a `MutationObserver` to `container`.
   - The observer records mutations (node additions, removals, attribute changes) that occur outside of React’s commit phase.

b. Mutation Buffer & ScheduleSafeCommit
   - Mutations are stored in a per‑root buffer. Before each commit, the scheduler invokes `scheduleSafeCommit(callback)` which:
     1. Flushes pending external mutations.
     2. Compares the current DOM snapshot with the expected fiber tree using a lightweight checksum (node type, key, and data‑reactroot attribute).
     3. If mismatches are detected, the commit is deferred and the fiber is marked with a `needsResync` flag.
   - Deferred commits are queued as microtasks (`Promise.resolve().then`) to run after any pending external changes.

c. Integration with Concurrent Scheduler
   - The new flag integrates with React’s existing `pauseWork`/`resumeWork` hooks, allowing the scheduler to pause rendering while external mutations are being processed.
   - During the render phase, components can call `useSyncExternalStore`‑style subscription `useExternalDOM()` to read a stable snapshot of the observed DOM state, ensuring no unnecessary re‑renders.

d. Error Boundary Enhancement
   - Extend the error boundary contract to catch commit‑phase DOM errors (`DOMException`, `InvariantViolation`). When caught, the boundary will trigger a forced re‑render of the affected subtree after the external mutation buffer is cleared.

e. Fallback Path
   - If a mutation cannot be reconciled (e.g., a required container node is removed), React will unmount the affected subtree and re‑mount it into a clean container, preserving overall UI stability.

f. Tests & Documentation
   - Add integration tests simulating Google Translate’s typical DOM rewrites (wrapping text nodes, inserting language‑specific spans).
   - Document the new API, migration steps, and best‑practice guidelines for sites that rely on external translation services.

4. Drawbacks
- Performance overhead: MutationObserver adds a small cost on every DOM change, and the checksum comparison introduces extra work during commits. Mitigation: observer is only active on roots created with `createRootWithSafety` and can be disabled via options.
- Increased complexity in the reconciler: New flags and buffers make the commit phase harder to reason about, potentially raising the risk of subtle bugs.
- Compatibility: Older browsers without MutationObserver would fallback to a no‑op observer, meaning the resilience feature would be unavailable, though core functionality remains unchanged.

5. Alternatives
- Encourage developers to disable Google Translate on React apps via `translate="no"` meta tags. This shifts responsibility to the app owner and does not solve cases where users manually trigger translation.
- Provide a community‑maintained polyfill that patches the DOM after translation, but this would be external to React and lack official support.
- Abort rendering when unexpected mutations are detected, showing a fallback UI. This is less graceful than the proposed recovery approach.

6. Unresolved Questions
- What is the optimal granularity for the checksum comparison (full subtree vs. per‑node) to balance accuracy and performance?
- How should the system handle mutations that occur during the render phase itself (e.g., a third‑party script modifies the DOM while React is rendering)?
- Should we expose a hook for library authors to opt‑out of the safety wrapper for performance‑critical roots?
- How will this interact with server‑side rendering hydration when the initial HTML has already been altered by translation services?
- Are there edge cases where the fallback unmount/remount could cause loss of component state that developers need to be warned about?

---

*RFC generated by Resurrection Bot 🧬*
