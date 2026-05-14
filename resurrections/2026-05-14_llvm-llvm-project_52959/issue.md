# Feature Request: Option to not check included files in clang-tidy

**Repository:** [llvm/llvm-project](https://github.com/llvm/llvm-project)
**Issue:** [llvm/llvm-project#52959](https://github.com/llvm/llvm-project/issues/52959)
**Reactions:** 41 👍
**Created:** 2022-01-02T22:27:45Z
**Last Activity:** 2025-10-02T21:03:35Z
**Labels:** enhancement, clang-tidy

---

## Original Description

When using `clang-tidy` to lint files, it needs to `#include` the dependencies. More often than not, however, dependencies are much larger and out of control of the consumer that is running `clang-tidy`.

`clang-tidy`, by default, currently does the correct thing and does not report errors/warnings from the `#include`d files. However, from watching it run, it's clearly still actually checking those files for errors (52k+ warnings suppressed!). This _dramatically_ increases the time it takes for `clang-tidy` to run from nearly instant to ~3 seconds for a large header file like `<napi.h>` (and this is a rather fast desktop). This really gets in the way of tools that integrate linters into code editors as every change requires that 3 second delay.

I see options about filtering headers or even lines but, at best, it looks like I'd need to list out every single range of my included header files which is actually a rather large number of files which could also change outside of my control. I have tried a variety of these options and not noticed a significant change in behavior in ways I care about.

Is there a way to do what I'd like? Or is there some fundamental reason why this wouldn't work? Frankly, it feels like this should even be the default.

---

*Resurrected by Resurrection Bot 🧬*
