# RFC: Support multiple formatters for a single file

1. Summary
VS Code will add native support for chaining multiple formatters on a single file. The new setting "editor.defaultFormatter" will accept an ordered array of formatter extension identifiers. At save (or on-demand), VS Code will invoke each formatter in sequence, aggregate their TextEdits, and apply the combined result. This RFC defines the FormatterChain class, the TextEditAggregator, and conflict‑resolution policies, while preserving backward compatibility with the existing single‑formatter behavior.

2. Motivation
Developers often rely on a combination of tools—e.g., Prettier for code style and ESLint --fix for lint‑rule enforcement. Currently they must manually run one after the other or configure one formatter to invoke the other, which is brittle and varies per language. Supporting multiple formatters natively eliminates custom scripts, reduces context‑switching, and ensures deterministic ordering across the ecosystem. Since VS Code 1.85 the FormattingEditProvider API now allows ordered chains, and LSP v3.17 introduces a "sequence" flag for documentFormatting, making a stable integration point feasible. Providing UI for ordering and clear conflict handling will improve developer productivity and encourage extensions to adopt the new protocol.

3. Detailed Design
   a. Settings Schema
      - Extend `editor.defaultFormatter` JSON schema to type: "array" of strings (extension identifiers). The existing string type remains accepted and is interpreted as a one‑element array.
      - Add `editor.formatOnSaveMode` options: "modifications", "full", and new "chain" (default "chain" when an array is present).
   b. FormatterChain Class
      ```ts
      class FormatterChain {
        private readonly formatters: IFormatter[];
        constructor(ids: string[], service: FormattingService) { /* resolve ids to providers */ }
        async format(document: TextDocument, options: FormattingOptions, token: CancellationToken): Promise<TextEdit[]> {
          let edits: TextEdit[] = [];
          for (const fmt of this.formatters) {
            const newEdits = await fmt.provideDocumentFormattingEdits(document, options, token);
            edits = TextEditAggregator.merge(edits, newEdits);
          }
          return ConflictResolver.resolve(edits);
        }
      }
      ```
   c. TextEditAggregator
      - Normalizes edits to the original document version, applying offset adjustments after each formatter.
      - Detects overlapping ranges; overlapping edits are queued for the ConflictResolver.
   d. ConflictResolver Module
      - Strategies: "lastWriterWins" (default), "merge" (attempts non‑destructive combination), and "abort" (fails the chain and reports to the user).
      - Configurable via `editor.formatterConflictStrategy`.
   e. Integration with Formatting Service
      - When a formatting request arrives, the service checks if the setting is an array. If so, it constructs a FormatterChain; otherwise, it falls back to the legacy single‑formatter path.
      - Save‑on‑type and format‑on‑paste continue to use the first formatter in the chain for performance, but users can opt‑in to full chaining via `editor.formatOnSaveMode`.
   f. UI Enhancements
      - Settings UI shows a list widget for "Default Formatter" when multiple entries are detected, supporting drag‑and‑drop ordering.
      - Each entry displays the extension’s display name and a preview of its enabled languages.
   g. Backward Compatibility
      - Existing configurations with a string value continue unchanged.
      - Extensions that do not declare the new "sequence" capability are ignored in a chain, and a warning is shown.

4. Drawbacks
   - Increased latency on save for files with long formatter chains, especially when each formatter performs heavy AST analysis.
   - Potential for subtle bugs if two formatters make contradictory changes; conflict resolution may produce unexpected results.
   - Extensions must update their manifests to declare the "sequence" capability, requiring coordination across the ecosystem.
   - Additional complexity in the core formatting service codebase, raising maintenance overhead.

5. Alternatives
   - Keep the status quo and rely on external scripts or tasks to run multiple formatters. This avoids core changes but places the burden on users.
   - Provide a single “meta‑formatter” extension that internally invokes other formatters. This centralizes logic but creates a single point of failure and limits UI integration.
   - Introduce a new LSP request that returns a combined edit set from the language server itself, bypassing VS Code chaining. This would work only for languages with a single server and does not address multi‑extension scenarios.

6. Unresolved Questions
   - What should be the default conflict resolution strategy for overlapping edits? The proposal suggests "lastWriterWins" but community feedback may prefer a safer "abort".
   - How to handle formatter-specific configuration (e.g., Prettier's tabWidth) when multiple formatters target the same language? Should we expose a per‑formatter config namespace?
   - Should we limit the maximum number of formatters in a chain to avoid pathological performance regressions?
   - How will telemetry be collected to measure the impact of chaining on save latency, and what thresholds will trigger warnings to users?
   - Will the drag‑and‑drop UI be accessible and work consistently across all platforms (web, desktop, remote)?

---

*RFC generated by Resurrection Bot 🧬*
