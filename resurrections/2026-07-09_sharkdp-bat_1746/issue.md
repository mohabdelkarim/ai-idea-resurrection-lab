# Support for different themes based on Terminal color scheme

**Repository:** [sharkdp/bat](https://github.com/sharkdp/bat)
**Issue:** [sharkdp/bat#1746](https://github.com/sharkdp/bat/issues/1746)
**Reactions:** 38 👍
**Created:** 2021-07-21T08:19:18Z
**Last Activity:** 2024-11-13T19:10:52Z
**Labels:** feature-request, help wanted

---

## Original Description

## Thanks!

As always and once again, thank you @sharkdp for your time and effort.  Hopefully I'm not being a nuisance with these requests.

## Homework

This is not a direct duplicate of #641 or #689, but it is related.  I think that `bat` can be improved beyond its current suggestion of manually running `defaults read` by performing actual detection of background colors, and exposing multiple theme options.

## Current State

Currently, `bat` allows specification of a SINGLE theme, via either `$BAT_THEME` or `--theme`.  This is great, and fits most use-cases.  The [README.md proposes a way to work around this](https://github.com/sharkdp/bat#dark-mode), which is macOS Terminal.app-specific, and a little hacky.  I think `bat` can do even better (and work on more platforms than macOS)!

When distributing tools built upon `bat`, it's not generally predictable what background color / terminal theme a user has configured for `{Terminal.app,iTerm2.app,Konsole,gnome-terminal,etc}`.

Additionally, the default theme (i.e. no `--theme` nor `$BAT_THEME`) may not be appropriate for a given terminal (and the work-around does not fix this).

Finally, the theme may actually need to change, if the user has multiple different terminal profiles, or if the color scheme of the profile changes based on external factors (such as the default Terminal.app theme, which may change based on the current time of day).

## Feature

It would be nice to have `bat` attempt to do some forms of auto-detection of the terminal's default background color, and allow the user to supply `$BAT_THEME_DARK` and `$BAT_THEME_LIGHT`, one of which is auto-selected by `bat`.

These should probably have lower precedence of `$BAT_THEME` and `--theme`.

There are several reasons for wanting this:

* Users who use macOS's "Auto" appearance switches between "Light" and "Dark" at various times of day, so a single theme isn't sufficient.
* Projects which build upon `bat` may want to provide *modified* themes (and cache, and .bin files) to work around features that `bat` doesn't have yet (e.g. #1745) and forcefully override e.g. `$BAT_THEME` with their modified theme.  These tools may wish to provide two themes -- one for light mode, and one for dark mode.

## Libraries and Other Prior Work

There are several projects that may be directly usable, or usable for inspiration and mechanism, for auto-detecting a light or dark terminal.

### `termbg`

Rust library that claims to do exactly what's needed.

However, it has at least one bug on macOS for Terminal.app: https://github.com/dalance/termbg/issues/8

https://github.com/dalance/termbg

### `rust-dark-light`

Rust project, not sure how well it works or what systems are supported.

https://github.com/frewsxcv/rust-dark-light

### `termenv`

While written in Go, this is a whole library for manipulating colors, and also features UNIX- and Windows-compatible light/dark mode detection.

In particular, it ha

---

*Resurrected by Resurrection Bot 🧬*
