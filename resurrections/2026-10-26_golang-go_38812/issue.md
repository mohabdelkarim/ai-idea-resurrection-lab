# cmd/go: "package … is not in GOROOT" is confusing in module mode when the package would exist in GOPATH mode

**Repository:** [golang/go](https://github.com/golang/go)
**Issue:** [golang/go#38812](https://github.com/golang/go/issues/38812)
**Reactions:** 88 👍
**Created:** 2020-05-02T16:28:26Z
**Last Activity:** 2026-03-26T15:20:53Z
**Labels:** NeedsInvestigation, FrozenDueToAge, GoCommand, modules

---

## Original Description

### What version of Go are you using (`go version`)?

<pre>
$ go version
go version go1.14.2 linux/amd64
</pre>

### Does this issue reproduce with the latest release?
Yes


### What operating system and processor architecture are you using (`go env`)?

<details><summary><code>go env</code> Output</summary><br><pre>
$ go env

</pre></details>

### What did you do?
If a parent folder contained a `go.mod` this overrides the GOPATH setting and there is no clear indication this is happening.
lets say the following exists in the file system
```
/work/go.mod 
```
and say you create a folder like
```
/work/projects/x/src/my/test2/main.go
```
and you export the GOPATH to point to your project
```
export GOPATH=/work/projects/x/
```
You will get an error like
```
can't load package: package my/test2 is not in GOROOT (/home/me/.gvm/gos/go1.14.2/src/my/test2)
```
And much time and head bashing will occur because you dont realize that go is using the `/work/go.mod` and overrides your `GOPATH` that you defined. This behavior is different then go 1.12 as well (it compiles without issue) so that adds to the confusion. (To be fair... I am totally guilty as sin for my own nasty creation, but there should be a better way of pointing out the root cause.)

### What did you expect to see?
It would be great to see some reference to the `go.mod` file in the error message and not the `GOROOT`. 
```
can't load package: package my/test2 is not in GOROOT (/home/me/.gvm/gos/go1.14.2/src/my/test2) with (/work/go.mod)
```
Or even more directly
```
can't load package: package my/test2 is not in go.mod (/work/my/test2)
```
I agree the former error is not wrong, but it is pointing in the wrong direction

### What did you see instead?
```
can't load package: package my/test2 is not in GOROOT (/home/me/.gvm/gos/go1.14.2/src/my/test2)
```

---

*Resurrected by Resurrection Bot 🧬*
