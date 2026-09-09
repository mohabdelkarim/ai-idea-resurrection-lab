# RFC: Consider re-licensing to AL v2.0, as RocksDB has just done

1. Summary
React, one of the most widely used UI libraries, is currently distributed under a BSD‑3‑Clause + Patents license. Recent industry trends and tooling improvements make a transition to a dual Apache‑2.0/GPL‑2.0‑only license feasible and beneficial. This RFC proposes to add a LICENSE.dual file containing the full Apache‑2.0 and GPL‑2.0 texts, to update the SPDX expression in package.json to "Apache-2.0 OR GPL-2.0-only", and to adjust CI, publishing, and documentation to support the dual‑license model.

2. Motivation
* **Legal alignment with ASF policies** – Many downstream projects (e.g., Apache Spark, Hadoop) require Apache‑2.0 compatibility. A dual license removes ambiguity for those ecosystems while preserving the ability for GPL‑2.0‑only users to integrate React under the strong copyleft model.
* **Patents protection continuity** – The Apache‑2.0 component retains the existing patent grant, addressing Meta’s concerns about losing patent coverage. The GPL‑2.0 side is offered as an option, not a replacement.
* **Tooling maturity** – SPDX now supports "OR" expressions, GitHub’s licensee, and ScanCode Toolkit can automatically verify dual licensing in CI, reducing administrative overhead.
* **Community precedent** – RocksDB, OpenTelemetry, and other high‑profile projects have successfully migrated to dual licensing, demonstrating that the model is well‑understood and accepted.
* **Strategic flexibility** – Dual licensing enables commercial entities that prefer permissive licenses to use Apache‑2.0, while open‑source purists can rely on GPL‑2.0, expanding React’s adoption surface.

3. Detailed Design
* **LICENSE.dual** – Create a new file at the repository root containing the full Apache‑2.0 license followed by the GPL‑2.0‑only license, each clearly demarcated.
* **package.json** – Change the "license" field to "Apache-2.0 OR GPL-2.0-only" and add a "licenseFile": "LICENSE.dual" entry for tooling compatibility.
* **CI integration** – Extend the existing GitHub Actions workflow:
  - Run `licensee --detect` to ensure the SPDX expression matches the repository contents.
  - Execute `scancode-toolkit` with a policy that flags missing or mismatched license headers.
* **Publishing pipeline** – Modify the npm publish script to bundle LICENSE.dual into the tarball and to set the `--license` flag accordingly.
* **Contribution workflow** – Update CONTRIBUTING.md with a section "Dual‑License Contributions" that explains that all contributions are automatically licensed under both Apache‑2.0 and GPL‑2.0‑only unless the contributor opts out via a DCO exception.
* **Fallback script** – Provide `scripts/strip-patent-clauses.js` that, when invoked, removes the patent clause from the generated distribution for environments that only accept pure Apache‑2.0 code (e.g., certain Linux distributions). The script is optional and gated behind a CI flag.

4. Drawbacks
* **Increased legal complexity** – Maintaining two licenses requires careful header management and may confuse newcomers.
* **Potential contributor friction** – Some contributors may be uncomfortable licensing under GPL‑2.0, necessitating clear opt‑out mechanisms.
* **Build artifact size** – Including two full license texts marginally increases package size, though the impact is negligible (<1 KB).
* **Compatibility edge cases** – Certain proprietary tools that only recognize a single SPDX identifier may need updates.

5. Alternatives
* **Stay with BSD+Patents** – Retain the status quo, avoiding any legal changes but missing out on Apache compatibility.
* **Switch to pure Apache‑2.0** – Simplify licensing but lose the copyleft option for GPL‑centric ecosystems.
* **Adopt MIT + Patent Grant** – A more permissive license, but would require a new patent clause and could be perceived as weaker protection.
* **Dual Apache‑2.0/LGPL‑2.1** – Offers a weaker copyleft option; however, LGPL‑2.1 introduces additional runtime linking requirements that complicate React’s bundling model.

6. Unresolved Questions
* **Contributor opt‑out process** – What exact mechanism (e.g., DCO footnote, CLA form) will be used to allow a contributor to decline GPL‑2.0 licensing?
* **Patent clause handling** – Should the fallback script strip only the patent paragraph or the entire clause? Legal review is needed.
* **Downstream audit** – How will major downstream projects (e.g., Next.js, Create React App) be notified and given time to adjust their compliance pipelines?
* **Governance approval** – What level of Meta legal sign‑off is required for a dual‑license change, and what timeline is realistic?
* **Impact on existing binaries** – Do we need to re‑release prior versions with the new dual license, or will the change apply only to future releases?
* **International considerations** – Are there jurisdictions where GPL‑2.0‑only may conflict with local open‑source policies, and how should we address them?

---

*RFC generated by Resurrection Bot 🧬*
