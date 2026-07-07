# Add `rustc --fatal` which stops at the first build error

**Repository:** [rust-lang/rust](https://github.com/rust-lang/rust)
**Issue:** [rust-lang/rust#27189](https://github.com/rust-lang/rust/issues/27189)
**Reactions:** 93 👍
**Created:** 2015-07-21T15:48:03Z
**Last Activity:** 2025-07-10T20:33:13Z
**Labels:** A-frontend, A-diagnostics, T-compiler, C-feature-request, D-verbose

---

## Original Description

(Should this be an RFC?)
## Motivation

When refactoring, one may have dozens or hundreds of build errors which need to be fixed one by one. Sometimes, a build error is only a consequence of an earlier error rather than something that need to be fixed itself:

``` rust
let foo = bar.method_that_was_renamed(); // First error
// ...
bar.other_method() // Second error because the type of `bar` is unknown
```

In such cases, it is a better strategy to start by looking at and fixing earlier errors (in the compiler output) first. The second error might just go away when the first is fixed.

In a large enough crate, it’s easy to get well over one screenful of compiler output. So the workflow is something like:
- Build. See lots of output be generated too fast to read.
- Scroll back to the beginning of the output for this build. Don’t miss it! It looks a lot like the output of the previous build.
- Find the first error.
- Try to fix the first error.
- Repeat.
## Proposal

Add a command-line argument to rustc, called something like `--fatal`. When it is given and the compile finds a build error (the kind that would cause the compilation to fail eventually, so not warnings), exit immediately after printing diagnostics for this error. This is the opposite of the usual strategy of finding as many errors as possible at once.

The new workflow is:
- Build.
- The first error is right there at the bottom of the terminal. A single error likely fits entirely on the screen.
- Try to fix it.
- Repeat.

(With some [inotify-based tricks](https://exyr.org/2011/inotify-run/), it’s not even necessary to switch focus from the terminal.)


---

*Resurrected by Resurrection Bot 🧬*
