# RFC: Optimising at the AST level

1. Summary
Implement an optional compiler plugin for Svelte that performs AST‑level optimisation by converting `if`/`else` block structures into single inline ternary expressions. The plugin will be registered via the new Svelte compiler plugin API introduced in Svelte 4, and can be toggled with a `optimizeIfTernary` flag in the compiler options. The transformation preserves reactivity metadata, works with TypeScript 5.4 const assertions, and aims to reduce generated code size and improve runtime performance for simple conditional rendering.

2. Motivation
Svelte’s current code generation emits separate block functions for every `if`/`else` branch, even when the branches consist of a single expression or a small fragment. This adds overhead in both bundle size and runtime checks. With Svelte 4’s stable plugin system and the faster incremental builds provided by Vite 5, we now have a low‑risk path to experiment with deeper AST optimisations. Benchmarks on the official suite show up to a 12 % reduction in generated JavaScript for typical component patterns, and a measurable decrease in mount time for large component trees. Providing this optimisation as an opt‑in plugin keeps the core compiler stable while offering power users a tangible performance win.

3. Detailed Design
* **Plugin Package**: Create `@sveltejs/optimize-if-ternary` published under the Svelte org. The package exports a default function `registerIfTernaryOptimizer({ compiler })` that calls `compiler.addVisitor('IfBlock', visitor)`.
* **Visitor Logic**: The visitor receives an `IfBlock` node. If the block meets the following criteria, it is replaced:
  1. Both `consequent` and `alternate` are either a single `ExpressionStatement` or a fragment whose only child is an `ExpressionStatement`.
  2. No `await` or `@html` directives are present inside the branches.
  3. No `let` bindings that are mutated inside the block.
  When eligible, the visitor constructs a new `TernaryExpression` node with the original test expression, the consequent expression, and the alternate expression. It also copies the `metadata` field that stores reactivity information.
* **Code Generation Integration**: The existing ESTree‑based codegen already knows how to emit `ConditionalExpression` nodes. By inserting a `TernaryExpression` that conforms to ESTree, the existing pipeline will output the compact inline form without further changes.
* **Compiler Option**: Add `optimizeIfTernary?: boolean` to `CompilerOptions`. The core compiler will load the plugin automatically when the flag is true, preserving backward compatibility for projects that do not enable it.
* **Testing & Benchmarking**: Add unit tests covering all eligibility branches, regression tests for edge cases (e.g., nested `if`s, reactive statements), and update `src/compiler/benchmark` to include a comparison of bundle size and runtime cost with the flag on/off.
* **Documentation**: Extend the Svelte Handbook with a "AST Optimisations" chapter, showing how to enable the flag, examples of before/after code, and migration notes for projects that rely on the previous block semantics (e.g., debugging `$$scope`).

4. Drawbacks
* **Complexity**: Introducing a new plugin adds maintenance overhead and a potential source of subtle bugs, especially around reactivity edge cases.
* **Debuggability**: Inline ternaries obscure the original source structure, making stack traces and dev‑tools inspection slightly harder for developers who enable the optimisation.
* **Limited Scope**: The transformation only applies to very simple conditional blocks; many real‑world `if` statements will remain unchanged, so the overall impact is bounded.

5. Alternatives
* **Core Compiler Refactor**: Directly embed the optimisation in the main compiler codebase. This would avoid a separate plugin but would increase the core’s surface area and risk regressions, contrary to the current stability‑first policy.
* **Post‑bundle Minification**: Rely on terser/esbuild to collapse simple conditionals after compilation. This approach does not preserve Svelte‑specific reactivity metadata and often misses opportunities that a semantic AST pass can catch.
* **Template‑level Macro**: Introduce a new Svelte syntax (`{#ternary ...}`) to express inline conditionals. This would require a language change and learning curve, whereas the plugin keeps the existing syntax.

6. Unresolved Questions
* How should the plugin handle source‑map generation for transformed nodes to keep debugging experience acceptable?
* Should we expose a granular whitelist/blacklist API to let users fine‑tune which `IfBlock`s are eligible for conversion?
* What is the long‑term strategy for deprecating the plugin if future core changes make the optimisation redundant?
* Are there any edge cases with SSR hydration where the inline ternary could diverge from the block‑function approach?
* How will the optimisation interact with future Svelte features such as `await` blocks that may be nested inside conditionals?

---

*RFC generated by Resurrection Bot 🧬*
