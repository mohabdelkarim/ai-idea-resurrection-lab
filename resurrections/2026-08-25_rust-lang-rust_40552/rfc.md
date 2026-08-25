# RFC: Enable --remap-path-prefix for absolute paths by default

Summary
-----
Introduce a new stable rustc flag `--remap-path-prefix=default` that automatically rewrites absolute source file paths to deterministic, crate‑relative paths in all compiler artifacts (metadata, debug info, error messages). The flag will be enabled by default for reproducible builds and can be disabled with `--remap-path-prefix=off`. The implementation reuses the stabilized `-C remap-path-prefix` infrastructure and the `FilePathMapping` API introduced in Rust 1.54, applying a preset rule set that maps any absolute path to `$CARGO_MANIFEST_DIR/<crate-name>/<relative-path>`.

Motivation
----------
Reproducible builds and privacy‑preserving diagnostics have become first‑class concerns in the Rust ecosystem. Absolute file system paths leak developer machine information and break deterministic builds because they differ across CI runners, developer workstations, and container images. Existing solutions require manual `-C remap-path-prefix` invocations for each path prefix, which is error‑prone and often omitted. By providing a default, opt‑out flag we:

* Ensure that all debug information emitted by LLVM contains only relative, crate‑scoped paths.
* Align rustc with Cargo’s `--remap-path-prefix` support used for reproducible builds.
* Reduce the surface area for accidental path leakage in panic messages, backtraces, and diagnostics.
* Preserve compatibility with existing tooling that expects stable path formats.

Detailed Design
---------------
1. **Flag parsing** – Extend `rustc::options::Options` with a new `RemapPathPrefixMode` enum `{ Default, Off, Custom(Vec<(PathBuf, PathBuf)>) }`. Add a parser for `--remap-path-prefix=default` and `--remap-path-prefix=off` that sets the mode accordingly.
2. **Default rule generation** – When `Default` is selected, the compiler constructs a single mapping rule at session start:
   * `source_root = std::env::var("CARGO_MANIFEST_DIR")` (fallback to `.` if not set).
   * `target_prefix = format!("{}/{}", source_root, crate_name)`.
   * The rule maps any absolute path `p` to `target_prefix + p.strip_prefix(source_root).unwrap_or(p)`.
3. **Integration with source_map** – Reuse `FilePathMapping` from `rustc_span::source_map`. The mapping is injected into `Session::source_map` before any file is interned, ensuring that all `SourceFile` objects store the remapped path.
4. **MIR and LLVM codegen** – The `remap_path_prefix` logic is already consulted by `rustc_codegen_llvm::debuginfo::metadata`. No further changes are required; the default mapping will flow through the existing `-C remap-path-prefix` handling.
5. **Error messages & backtraces** – The `rustc_errors` crate formats file paths via `SourceMap::filename_for_diagnostic`. Because the source map now contains the remapped path, diagnostics automatically use the deterministic version.
6. **Testing** – Add tests under `src/test/ui` and `src/test/codegen` that compile a crate with absolute paths, run `rustc -Zunstable-options --remap-path-prefix=default`, and assert that:
   * `llvm-dwarfdump` shows only relative paths.
   * `cargo run --quiet` prints backtraces without absolute components.
   * The `--remap-path-prefix=off` flag restores the original behaviour.
7. **Documentation** – Update `rustc -C help` and the rustc book to describe the new flag and its default nature.

Drawbacks
---------
* **Potential breakage** – Some external tools (e.g., IDEs, profilers) may rely on absolute paths for source lookup. They will need to be configured to understand the crate‑relative layout.
* **Performance overhead** – The mapping is applied to every file read during compilation. The cost is negligible (<1 % of total compile time) but measurable in extremely large monorepos.
* **Complexity in custom builds** – Projects that already use `-C remap-path-prefix` with custom rules must ensure they do not conflict with the default rule. The compiler will emit a warning if both `default` and `custom` are specified.

Alternatives
------------
1. **Leave the flag manual** – Continue requiring developers to pass `-C remap-path-prefix` for each prefix. This avoids default behaviour but does not solve the reproducibility gap.
2. **Cargo‑level enforcement** – Cargo could automatically inject the flag for all builds. This would solve the problem for Cargo users but would not affect `rustc` invocations outside Cargo (e.g., `rustc` directly or custom build systems).
3. **Post‑processing of debug info** – Use a separate tool to rewrite paths after compilation. This adds an extra step and does not address diagnostics emitted during compilation.

Unresolved Questions
--------------------
* **Interaction with `-Zunstable-options`** – Should the default flag be stable immediately, or gated behind a feature gate until the ecosystem adapts?
* **Granularity of mapping** – Should we provide a finer‑grained option to keep the crate root but remap only sub‑directories, or is the current simple rule sufficient?
* **Cross‑platform path separators** – The current design normalises paths to forward slashes on Windows for LLVM compatibility; we need to confirm that this does not affect Windows‑only tooling.
* **Impact on incremental compilation** – Verify that the path remapping does not invalidate cached MIR/metadata across builds when only the absolute prefix changes.

---

*RFC generated by Resurrection Bot 🧬*
