# RFC: Exclude files or directories from editor.formatOnSave

Summary
-----
Introduce a new user‑setting `editor.formatOnSaveExclude` that accepts an array of glob patterns. The setting allows users to specify files or directories that should be ignored by the built‑in `editor.formatOnSave` pipeline. When a document is saved, the SaveParticipant checks this list before invoking any `FormattingEditProvider`. This RFC details the motivation, design, drawbacks, alternatives, and open questions for the feature.

Motivation
----------
Developers frequently work with generated files (e.g., minified JavaScript, compiled CSS, protobuf stubs) or configuration files that should not be automatically formatted. The lack of an exclusion mechanism forces users to disable `formatOnSave` globally or rely on fragile work‑arounds such as per‑language toggles that affect unrelated files. Since VS Code 2024 added native glob handling in `settings.json` and the formatting pipeline now supports per‑resource toggles, we have the technical foundation to implement a robust exclusion API without breaking existing formatters. Providing a first‑class exclusion list improves developer ergonomics, reduces accidental changes to generated artifacts, and aligns VS Code with other editors that already support similar features.

Detailed Design
---------------
1. **Setting Schema**
   - Add `editor.formatOnSaveExclude` to `settings.schema.json`.
   - Type: `array` of `string`.
   - Each string is a glob pattern resolved relative to the workspace root.
   - Example: `["**/dist/**", "**/*.min.js", ".vscode/**"]`.
2. **Configuration Retrieval**
   - Extend `FormattingEditProvider` interface with a new method `shouldFormat(resource: Uri): boolean` (default implementation reads the setting).
   - The SaveParticipant obtains the setting via `workspace.getConfiguration('editor').get<string[]>('formatOnSaveExclude')`.
3. **Glob Matching**
   - Reuse VS Code’s built‑in `GlobMatcher` (introduced in 2024) to test the saved document’s URI against the exclude list.
   - Matching is case‑insensitive on Windows, case‑sensitive otherwise.
4. **Save Flow Modification**
   - In `src/vs/editor/contrib/format/formatOnSaveParticipant.ts`, before invoking any formatter, call `if (excludeMatcher.matches(document.uri)) return;`.
   - Preserve existing language‑specific `editor.formatOnSave` toggles; exclusion takes precedence.
5. **Workspace Trust**
   - The exclusion list is only applied in trusted workspaces, mirroring the current behavior of `formatOnSave`.
6. **Testing**
   - Add unit tests in `formatOnSave.test.ts` covering:
     * Simple glob exclusion.
     * Overlapping patterns.
     * Interaction with `editor.formatOnSave` per‑language settings.
     * Trust boundaries.
7. **Documentation**
   - Update the Settings UI, add a description in the Settings editor, and provide a link to a usage guide.

Drawbacks
--------
- **Performance**: Introducing glob matching on every save adds a small overhead, especially in large workspaces with many patterns. The impact is mitigated by caching compiled glob objects.
- **Complexity**: The new API expands the formatting pipeline, requiring formatter extensions to be aware of the new `shouldFormat` hook for custom behavior. Existing extensions will continue to work unchanged, but future maintainers must understand the exclusion flow.
- **User Confusion**: Users may create overlapping include/exclude patterns, leading to unexpected results. Clear documentation and UI validation are required to minimise this risk.

Alternatives
-----------
1. **Per‑language exclude list** – Add `editor.formatOnSaveExclude` under each language identifier. This would increase configuration noise and duplicate logic already handled by the global list.
2. **Extension‑only API** – Expose a command `editor.toggleFormatOnSave` that extensions could call to disable formatting for specific resources. This places the burden on extensions rather than providing a native, user‑driven solution.
3. **File‑type based disabling** – Use `files.exclude` to hide files from the explorer and implicitly skip formatting. This is indirect and does not cover cases where a file is visible but should still be excluded.
The chosen approach (global glob list) offers the simplest UX while leveraging existing glob infrastructure.

Unresolved Questions
-------------------
- **Pattern precedence**: Should later entries in the array override earlier ones, or is the list evaluated purely as a set? The current proposal treats it as a set; we need consensus.
- **Workspace folder scopes**: In multi‑root workspaces, do patterns apply to each folder individually or globally? The design assumes global relative to each folder, but edge cases need clarification.
- **Telemetry**: Should we emit usage telemetry for the new setting? If so, what granularity is appropriate without violating privacy?
- **Interaction with `editor.codeActionsOnSave`**: Ensure that exclusion does not unintentionally skip other on‑save actions that rely on formatting results.
- **Future extensibility**: How will we expose this exclusion list to extensions that implement their own formatting pipelines? A stable API surface must be defined.

---

*RFC generated by Resurrection Bot 🧬*
