# proposal: spec: lazy values

**Repository:** [golang/go](https://github.com/golang/go)
**Issue:** [golang/go#37739](https://github.com/golang/go/issues/37739)
**Reactions:** 104 👍
**Created:** 2020-03-07T21:39:43Z
**Last Activity:** 2026-04-08T21:30:22Z
**Labels:** LanguageChange, Proposal, LanguageChangeReview

---

## Original Description

This is just a thought.  I'm interested in what people think.

Background:

Go has two short circuit binary operators, `&&` and `||`, that only evaluate their second operand under certain conditions.  There are periodic requests for additional short circuit expressions, often but not only the `?:` ternary operator found originally in C; for example: #20774, #23248, #31659, #32860, #33171, #36303, #37165.

There are also uses for short circuit operation in cases like conditional logging, in which the operands to a logging function are only evaluated if the function will actually log something.  For example, calls like

```Go
    log.Verbose("graph depth %d", GraphDepth(g))
```

where `log.Verbose` only logs a message if some command line flag is specified, and `GraphDepth` is an expensive operation.

To be clear, all short circuit operations can be expressed using `if ` statements (or occasionally `&&` or `||` operators).  But this expression is inevitably more verbose, and can on occasion overwhelm more important elements of the code.

```Go
    if log.VerboseLogging() {
        log.Verbose("graph depth %d", GraphDepth(g))
    }
```

In this proposal I consider a general mechanism for short circuiting.

Discussion:

Short circuiting means delaying the evaluation of an expression until and unless the value of that expression is needed.  If the value of the expression is never needed, then the expression is never evaluated.

(In this discussion it is important to clearly understand the distinction that Go draws between expressions (https://golang.org/ref/spec#Expressions) and statements (https://golang.org/ref/spec#Statements).  I'm not going to elaborate on that here but be aware that when I write "expression" I definitely do not mean "statement".)

In practice the only case where we are interested in delaying the evaluation of an expression is if the expression is a function call.  All expressions other than function calls complete in small bounded time and have no side effects (other than memory allocation and panicking).  While it may occasionally be nice to skip the evaluation of such an expression, it will rarely make a difference in program behavior and will rarely take a noticeable amount of time.  It's not worth changing the language to short circuit the evaluation of any expression other than a function call.

Similarly, in practice the only case where we are interested in delaying the evaluation of an expression is when passing that expression to a function.  In all other cases the expression is evaluated in the course of executing the statement or larger expression in which it appears (other than, of course, the `&&` and `||` operators).  There is no point to delaying the evaluation of expression when it is going to be evaluated very shortly in any case.  (Here I am intentionally ignoring the possibility of adding additional short circuit operators, like `?:`, to the language; the language does not have t

---

*Resurrected by Resurrection Bot 🧬*
