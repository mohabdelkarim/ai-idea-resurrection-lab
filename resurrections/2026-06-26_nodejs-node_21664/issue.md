# Ability to replace current Node process with another

**Repository:** [nodejs/node](https://github.com/nodejs/node)
**Issue:** [nodejs/node#21664](https://github.com/nodejs/node/issues/21664)
**Reactions:** 24 👍
**Created:** 2018-07-05T03:36:31Z
**Last Activity:** 2025-06-25T07:38:06Z
**Labels:** child_process, feature request, stale

---

## Original Description

**Edit:** If someone can come up with a better shim for `execve` for Windows, that'd be *far* better. The form below is *very* expensive and *very* horrible.

**Edit 2:** Linked relevant [SO question](https://stackoverflow.com/questions/51185115/what-is-the-ideal-way-to-emulate-process-replacement-on-windows).

**Edit 3:** Clarify FS changes

**Edit 4:** Here's the text from that SO question as of July 6, 2018 (so you don't have to search for it), where I asked about how to do the Windows part.

<details>
<summary>Click to show (warning: lots of text)</summary>

So, in a [feature request I filed against Node.js](https://github.com/nodejs/node/issues/21664), I was looking for a way to replace the current Node process with another. In Linux and friends (really, any POSIX-compliant system), this is easy: use [`execve`](http://man7.org/linux/man-pages/man2/execve.2.html) and friends and call it a day. But obviously, that won't work on Windows, since it only has `CreateProcess` (which `execve` and friends delegate to, [complete with async behavior](https://stackoverflow.com/questions/49736973/blocking-version-of-execvp-windows)). And it's not like [people](https://stackoverflow.com/questions/35111313/windows-exec-equivalent) [haven't](https://stackoverflow.com/questions/6743567/replace-current-process-with-invocation-of-subprocess) [wanted](https://stackoverflow.com/questions/7198666/strategies-for-replacing-program-executable-in-windows) [to](https://stackoverflow.com/questions/198122/how-can-i-replace-the-current-java-process-like-a-unix-style-exec) [do](https://stackoverflow.com/questions/5450147/how-to-replace-the-current-java-process-in-windows-using-jna-jni) [similar](https://stackoverflow.com/questions/45607959/restart-windows-process-inplace-preserving-process-id-and-handles), leading to [numerous duplicate questions on this site](https://www.google.com/search?q=windows+replace+current+process+site:stackoverflow.com). (This isn't a duplicate because it's explicitly seeking a workaround given certain constraints, not just asking for direct replacement.)

Process replacement has several facets that have to addressed:

1. All console I/O streams have to be forwarded to the new process.
1. All signals need transparently forwarded to the new process.
1. The data from the old process have to be destroyed, with as many resources reclaimed as possible.
1. All pre-existing threads and child processes should be destroyed.
1. All pre-existing handles should be destroyed apart from open file descriptors and named pipes/etc.
1. Optimally, the old process's memory should be kept to a minimum after the process is created.
1. For my particular use case, retaining the process ID is not important.

And for my particular case, there are a few constraints:

1. I can control the initial process's startup as well as the location of my "process replacement" function.
1. I could load arbitrary native code via add-ons at potentially any stack

---

*Resurrected by Resurrection Bot 🧬*
