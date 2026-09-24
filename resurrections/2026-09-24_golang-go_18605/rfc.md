# RFC: proposal: spec: allow x, y..., z in list for variadic function argument

Summary
Allow mixing explicit arguments with a spliced slice in variadic function calls using the ellipsis syntax. The new syntax permits calls such as fmt.Printf("%d %d %d", a, b, s... ) where s is a []int and a, b are individual int arguments. The feature is gated behind the goexperiment.VariadicSplice flag and includes compiler, gofmt, and vet support.

Motivation
Current Go rules require that either all variadic arguments are supplied individually, or a single slice is supplied with an ellipsis. This restriction forces developers to allocate a temporary slice when they need a mixture of explicit values and a slice, e.g.,
    args := []int{c, d}
    fmt.Printf("%d %d %d %d", a, b, args...)
The temporary allocation adds overhead and clutters code. With generics now in the language, many patterns that previously needed this workaround are more common, increasing the desire for a concise mixed‑argument form. The proposal leverages recent improvements in the AST, type checker, and diagnostics to keep the implementation safe while improving ergonomics for real‑world code.

Detailed Design
1. Syntax: In a call expression, any argument that is a slice expression followed immediately by an ellipsis token ( ... ) is parsed as a VariadicSpliceExpr. The grammar change is minimal: argument ::= expression | sliceExpr "...".
2. AST: Introduce a new node type `VariadicSpliceExpr` that embeds the underlying slice expression. The existing `CallExpr` node now holds a slice of `Expr` where each element may be a `VariadicSpliceExpr`.
3. Parser: Extend the parser to detect the pattern `X...` where X's type is a slice. When the experiment flag is on, the parser builds a `VariadicSpliceExpr`; otherwise it reports a syntax error matching the current language spec.
4. Type Checker: When checking a call to a variadic function `func f(t ...T)`, each argument is examined. A `VariadicSpliceExpr` is type‑checked as a slice of `T`. The checker ensures that the element type of the slice is assignable to `T`. Mixed explicit arguments are type‑checked individually as before.
5. Code Generation: The backend emits code that:
   a. Allocates a temporary slice of length equal to the number of explicit variadic arguments plus the length of the spliced slice.
   b. Stores each explicit argument into the temporary slice.
   c. Calls the runtime `append` to concatenate the spliced slice.
   d. Passes the resulting slice to the variadic function using the existing variadic call convention.
   This algorithm reuses the existing `append` runtime routine, keeping the generated code simple.
6. Tooling:
   * gofmt: Formats `s...` exactly as before, preserving spacing.
   * go vet: Adds a check `vetVariadicSplice` that warns when the spliced slice is nil or when the total argument count exceeds a configurable limit.
   * go test: New test cases in `src/testing` cover empty slices, nil slices, and mixed arguments across packages.
   * Experiment flag: The feature is enabled with `-gcflags=all=-goexperiment=VariadicSplice` and disabled by default.

Drawbacks
* Increased compiler complexity: The parser, type checker, and backend each need new paths, raising maintenance burden.
* Potential for subtle bugs: Mixing explicit and spliced arguments can hide off‑by‑one errors if a developer unintentionally includes an extra argument.
* Runtime overhead: The temporary slice allocation adds a small cost, though it is comparable to the current manual workaround.
* Backward compatibility: Existing code that mistakenly relied on the current error for `s...` will now compile, possibly surfacing latent logic errors.

Alternatives
1. Keep the status quo and require developers to create a temporary slice manually. This avoids any language change but retains the ergonomic cost.
2. Introduce a built‑in helper function `variadic.Splice(f, args..., slice...)` that performs the concatenation at runtime. This would avoid compiler changes but adds a library dependency and less syntactic clarity.
3. Use generics to define a wrapper variadic function that accepts a slice and individual arguments, e.g., `func PrintfMixed[T any](format string, first T, rest ...T)`. This works for homogeneous types but does not solve mixed‑type variadic functions like `fmt.Printf`.

Unresolved Questions
* Should the feature be allowed for variadic parameters of interface type only, or for any concrete type? The current design permits any type, but edge cases with type parameters need further review.
* How should the compiler handle a spliced slice that is itself the result of a function call with side effects? The order of evaluation must be defined to match Go's left‑to‑right argument evaluation rules.
* Is there a need for a lint rule to discourage excessive mixing of explicit and spliced arguments for readability? The proposal leaves this to future vet enhancements.
* Performance impact on hot paths: Benchmarks are needed to quantify the overhead of the temporary slice versus the manual allocation pattern.

---

*RFC generated by Resurrection Bot 🧬*
