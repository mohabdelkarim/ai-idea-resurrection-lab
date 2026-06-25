# [feat] upstream nix requirements to nixpkgs

**Repository:** [tauri-apps/tauri](https://github.com/tauri-apps/tauri)
**Issue:** [tauri-apps/tauri#8588](https://github.com/tauri-apps/tauri/issues/8588)
**Reactions:** 6 👍
**Created:** 2024-01-11T10:28:19Z
**Last Activity:** 2025-09-03T12:13:49Z
**Labels:** help wanted, type: feature request, platform: Nix/NixOS

---

## Original Description

### Describe the problem

Not sure if this is a bug or a feature, it's borderline imo.

Basically what I expect is that when i use the `cargo-tauri` derivation from `nixpkgs` that i don't also have to copy and paste a bunch of additional prerequisites from the tauri docs in order to get things half working.

I say half working because I'm still running into bugs with `cargo-tauri`, especially on mac, one of which i already pushed a fix for https://github.com/NixOS/nixpkgs/pull/279771#event-11446551011

I also see that one of the dependencies, `webkitgtk` is marked as broken in `nixpkgs` on mac, but listed as a dependency on the tauri docs. I understand the nix docs say nixos rather than `nix` but it's pretty common use case for people working on linux/mac to be using nix rather than committing to a full nixos setup.

Additionally, I noticed that the prerequisites in the docs only work for a `nix develop` style shell, they don't work for `nix run`, say if I wanted to lift some standard tauri tasks into a package, the instructions don't cover that. This is because the additional steps of setting up the library etc. are limited to a `shellHook`.

Further, the prerequisites are missing required steps in the `shellHook`. We found that when tauri is built via nix there is a need to disable webkit compositing mode like `export WEBKIT_DISABLE_COMPOSITING_MODE=1` in the `shellHook`. This seems to be some known tribal knowledge, as it appears in snippets from other people such as https://github.com/tauri-apps/tauri/issues/8535 but it's not listed in the prerequisites in the docs.

There are other issues like https://github.com/tauri-apps/tauri/issues/8535 that I expect are probably not issues with tauri itself, but some additional work that needs to be done on the nix side. At the moment it isn't clear where to put or discuss such a fix, would it just result in more documented boilerplate? or is there a way to codify it?

Stepping back a bit, I feel like the meta issue is that fixes to issues are being pushed into the tauri docs (or not) rather than some derivation that is directly maintainable and reusable downstream.

### Describe the solution you'd like

Tauri maintains the derivation in `nixpkgs` with the same dependencies that it outlines in the documentation, so then there are no manual steps for consumers.

### Alternatives considered

Another alternative would be that tauri maintains their own nix code separate to nixpkgs, such as an overlay or flake.

This would be fine too, the main problem to solve is to lift dependencies and other issues from docs and into nix-compatible code somewhere.

### Additional context

_No response_

---

*Resurrected by Resurrection Bot 🧬*
