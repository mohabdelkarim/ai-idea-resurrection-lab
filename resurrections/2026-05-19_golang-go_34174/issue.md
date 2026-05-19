# proposal: Go 2: string interpolation

**Repository:** [golang/go](https://github.com/golang/go)
**Issue:** [golang/go#34174](https://github.com/golang/go/issues/34174)
**Reactions:** 523 👍
**Created:** 2019-09-08T10:45:23Z
**Last Activity:** 2024-02-08T16:52:06Z
**Labels:** LanguageChange, v2, Proposal, Proposal-FinalCommentPeriod

---

## Original Description

# Introduction 

For ones who don't know what it is:

#### Swift
```swift
let multiplier = 3
let message = "\(multiplier) times 2.5 is \(Double(multiplier) * 2.5)"
// message is "3 times 2.5 is 7.5"
```

#### Kotlin
```kotlin
var age = 21

println("My Age Is: $age")
```

#### C#
```c#
string name = "Mark";
var date = DateTime.Now;

Console.WriteLine($"Hello, {name}! Today is {date.DayOfWeek}, it's {date:HH:mm} now.");
```

# Reasoning of string interpolation vs old school formatting

I used to think it was a gimmick but it is not in fact. It is actually a way to provide type safety for string formatting. I mean compiler can expand interpolated strings into expressions and perform all kind of type checking needed.

### Examples

```
variable := "var"
res := "123\{variable}321" // res := "123" + variable + "321"
```

```
return errors.New("opening config file: \\{err}") // return errors.New("opening config file: " + err.Error())
```

```
var status fmt.Stringer
…
msg := "exit status: \{status}" // msg := "exit status: " + status.String()
```

```
v := 123
res := "value = \{v}" // res := "value = " + someIntToStringConversionFunc(v)
```

# Syntax proposed

* Using `$` or `{}` would be more convenient in my opinion, but we can't use them for compatibility reasons
* Using Swift `\(…)` notation would be compatible but these `\()` are a bit too stealthy

I guess  `{…}` and `\(…)` can be combined into `\{…}`

So, the interpolation of variable `variable` into some string may look like

```
"<prefix>\{variable}<suffix>"
```

Formatting also has formatting options. It may look like

```
"<prefix>\{variable[:<options>]}<suffix>"
```

#### Examples of options

```
v := 123.45
fmt.Println("value=\{v:04.3}") // value=0123.450
```

```
v := "value"
fmt.Println("value='\{v:a50}'") // value='<45 spaces>value'
```

etc

# Conversions

There should be conversions and formatting support for built in types and for types implementing `error` and `fmt.Stringer`. Support for types implementing

```
type Formatter interface {
    Format(format string) string
}
```

can be introduced later to deal with interpolation options

# Pros and cons over traditional formatting

### Pros

* Type safety
* Performance (depends on the compiler)
* Custom formatting options support for user defined types

### Cons

* Complication of a compiler
* Less formatting methods supported (no `%v` (?), `%T`, etc)

---

*Resurrected by Resurrection Bot 🧬*
