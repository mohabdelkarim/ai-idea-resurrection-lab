# No, I dont want share history.

**Repository:** [ohmyzsh/ohmyzsh](https://github.com/ohmyzsh/ohmyzsh)
**Issue:** [ohmyzsh/ohmyzsh#2537](https://github.com/ohmyzsh/ohmyzsh/issues/2537)
**Reactions:** 190 👍
**Created:** 2014-02-16T15:08:44Z
**Last Activity:** 2024-11-22T08:21:55Z
**Labels:** 

---

## Original Description

------
### SOLUTION

~~The solution to this is appending the command `unsetopt share_history` to your zshrc file (make sure to put it at the bottom of the file; that is, _after_ OMZ has been loaded).~~

~~2376022 removed `share_history `from OMZ. Just `omz update`.~~ I reverted the change. You can still fix this by putting `unsetopt share_history` in your zshrc file, after OMZ is loaded.

-- @mcornella

------
you have 

> setopt share_history

on libs/history.szh.

The thing is that once enable there no seems to be a way to disable it. On my .zshrc I tried appending at the end of file:

> setopt share_history Off
> setopt share_history 0

It doesnt work, the only way is disabling it on the history.zsh file but.. that means i wont get updates for it =)

So what is the correct way? are you sure users expect this to be enabled by default?? It's very anoying for me


---

*Resurrected by Resurrection Bot 🧬*
