# Why don't Ctrl+Backspace and Ctrl+Delete work?

**Repository:** [ohmyzsh/ohmyzsh](https://github.com/ohmyzsh/ohmyzsh)
**Issue:** [ohmyzsh/ohmyzsh#7609](https://github.com/ohmyzsh/ohmyzsh/issues/7609)
**Reactions:** 52 👍
**Created:** 2019-02-19T12:42:36Z
**Last Activity:** 2022-11-16T04:48:23Z
**Labels:** Topic: bindkey

---

## Original Description

It is standard in UI applications to have Ctrl+Backspace delete a word before the cursor (`backwards-kill-word`) and Ctrl+Delete delete a words after the cursor (`kill-word`). In Oh-My-ZSH I can use Alt+Backspace and Ctrl+W for the former and there doesn't seem to be an alternative for the latter. Why is that?

It is very easy to implement the standard behavior, I could just add these lines to `lib/key-bindings.zsh`:
```
bindkey '^H' backward-kill-word
bindkey '^[[3;5~' kill-word
```
But before doing so, I'm interested whether there is a reason not to add this.

---

*Resurrected by Resurrection Bot 🧬*
