# proposal: spec: allow x, y..., z in list for variadic function argument

**Repository:** [golang/go](https://github.com/golang/go)
**Issue:** [golang/go#18605](https://github.com/golang/go/issues/18605)
**Reactions:** 92 👍
**Created:** 2017-01-11T04:17:55Z
**Last Activity:** 2024-08-22T18:13:46Z
**Labels:** LanguageChange, v2, Proposal, NeedsDecision, FrozenDueToAge, dotdotdot

---

## Original Description

(See the bottom of this post for a full example.) This is something I've run into a few times and I've been unable to find a discussion fully explaining why it can't/shouldn't be supported.

I've tried searching for prior discussion about this and have mostly come up with Stack Overflow questions where people have been confused about the current restriction. The best reasoning I've found is in #2873:

> To avoid confusion about what slice is being passed, the ... syntax only applies when it is providing the entire ... argument; you can't splice in additional parameters with it.

I disagree with this. It implies the developer is already expected to understand that 1) `...string` denotes a slice and 2) there would be two slices (i.e., your variadic arguments were turned into a slice implicitly).

They could also be expected to understand that the second slice (`paths` in my example below) is appended to the first slice if you were to mix the two approaches. I would even argue that is the expected behavior.

Ultimately, if Go was to support this proposal there are (AFAICT) still only two possible outcomes:

1. The slice followed by `...` is passed on as-is (0 positional arguments)
2. A new slice is implicitly created (>0 positional arguments)

This proposal extends the second case to also implicitly append the slice followed by `...` to the implicit slice (approximately what I've done as a workaround in the example below).

One new behavior resulting from this is that modifying some values in the resulting slice will have no outside effect, while modifying the indexes at the end that correspond to the passed-in slice may modify it. I don't think this is very different from today however, as there is currently no way to know if modifying any index in the argument slice will have any outside effect or not, so touching it should be strongly discouraged regardless. For such cases, an explicit slice should always be passed instead.

### Full example

```go
package main

import (
    "bytes"
    "fmt"
    "os/exec"
)

func main() {
    list("/usr/share", "/var/tmp")
}

func list(paths ...string) {
    // Desired:
    //cmd := exec.Command("ls", "-la", paths...)
    // Current workaround:
    cmd := exec.Command("ls", append([]string{"-la"}, paths...)...)
    var out bytes.Buffer
    cmd.Stdout = &out
    err := cmd.Run()
    if err != nil {
        fmt.Printf("error: %v\n", err)
    }
    fmt.Println(out.String())
}
```

---

*Resurrected by Resurrection Bot 🧬*
