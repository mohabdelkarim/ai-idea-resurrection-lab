# Support multiple windows

**Repository:** [alacritty/alacritty](https://github.com/alacritty/alacritty)
**Issue:** [alacritty/alacritty#607](https://github.com/alacritty/alacritty/issues/607)
**Reactions:** 491 👍
**Created:** 2017-06-11T06:33:40Z
**Last Activity:** 2022-12-29T15:03:07Z
**Labels:** enhancement, help wanted

---

## Original Description

I use a window manager instead of tmux. With other terminal emulators when I want a new terminal instance, I simply open a new window. As far as I can tell, the only way to accomplish this with Alacritty is to open a new instance of the application. This is inferior for three reasons:

1. Load times when opening a new instance of Alacritty are subpar. For a program that prides itself on being the fastest, opening new terminals should be no exception. (Loading a new instance of Alacritty lasts about 1 second for me vs instant when opening a new window in iTerm.)

2. On macOS opening multiple instances of Alacritty fills up the Dock and Application Switcher.

3. Currently, such behavior must be implemented manually by the user.

From what I can tell from other issues, using window managers as a replacement for tmux is within Alacritty's scope. Even when using tmux, it can be desirable to open a second tmux instance for an unrelated session without detaching from the current session. I think multiple windows should be supported natively by Alacritty.

---

*Resurrected by Resurrection Bot 🧬*
