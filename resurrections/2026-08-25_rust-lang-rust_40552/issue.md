# Enable --remap-path-prefix for absolute paths by default

**Repository:** [rust-lang/rust](https://github.com/rust-lang/rust)
**Issue:** [rust-lang/rust#40552](https://github.com/rust-lang/rust/issues/40552)
**Reactions:** 81 👍
**Created:** 2017-03-15T18:30:22Z
**Last Activity:** 2023-06-16T16:37:48Z
**Labels:** T-compiler, C-feature-request

---

## Original Description

According to #40374 , a part of private information is leaked by the path string living in the compiled binaries. To protect privacy and help debugging, I think we can let rustc to mangle the path. Here is my solution:

Basically, we can hide the 'insignificant' part of the path (which usually contains some private and/or unrelated info), leave 'significant' part untouched. Then what is the 'significant' part of a path? Here is an example: Assume that we have a project `foobar` which is in user's home directory (here I use a windows path, on *nix things work similarly):
```
C:\Users\username\Documents\foobar
```
In this case, the useful part is the crate name and the part after the crate name, i.e.
```
\foobar\lib.rs
```
Assuming we have a mod called 'somemod', then after mangling, the new path looks like:
```
[crate]\foobar\somemod\mod.rs
```
which not only saves the relatitionship information between sources files, but also protects the privacy of the user (since no more user name or aboslute path exists) !

The next question is how to process all paths under this rule. From what I know, all compiled code of a crate comes from 4 sources:
* crates.io or mirrors of crates.io, or some independent 3rd party repo, in which the code is cached and lives in the cargo cache directory
* remote git repositories
* local filesystem
* the crate itself (which may locate at any place)

We could specify different root names for these sources to indicate their origin:
* For code from crates.io or mirrors, the root name is `[crates.io]`. Example:
`C:\Users\username\.cargo\registry\src\github.com-1ecc6299db9ec823\winapi-0.2.8\` will be mangled to `[crate.io]\winapi-0.2.8\`
* For code from remote git repository, the root name is `[username@git server name]`. Example: `https://github.com/rust-lang/rust` will be manged to `[rust-lang@github.com]/rust`
* For code from local filesystem, the root name is `[local]`. Example: `D:\workspaces\foobarng\` will be mangled to `[local]\foobarng\`
* For code from the crate itself, the root name is `crate`. Example: `C:\Users\username\Documents\foobar\` will be mangled to `[crate]\foobar\`

And for helping debuggers, all paths in debugging information won't be modified. Thus, users still know where the debugging code is, and won't worry about leaking privacy (just need stripping out debugging information before packaging on *nix, or not distributing .pdb files on windows).

---

*Resurrected by Resurrection Bot 🧬*
