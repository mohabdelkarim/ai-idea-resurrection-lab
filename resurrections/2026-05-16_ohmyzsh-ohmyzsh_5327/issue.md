# oh-my-zsh very slow :(

**Repository:** [ohmyzsh/ohmyzsh](https://github.com/ohmyzsh/ohmyzsh)
**Issue:** [ohmyzsh/ohmyzsh#5327](https://github.com/ohmyzsh/ohmyzsh/issues/5327)
**Reactions:** 139 👍
**Created:** 2016-08-20T18:48:54Z
**Last Activity:** 2024-07-08T03:46:48Z
**Labels:** 

---

## Original Description

Hello,

I'm new to zsh/oh-my-zsh and installed it the first time on Mac OS X today. My Terminal (iTerm2 and default Mac-Terminal) starts very slow now - I have a real "waiting" time after opening App. Inside the Terminal it's better but also compared to "default bash" - slow. For example, if I only push the enter-key it just takes 1-2 seconds before terminal "responds", or if I press "CMD+V" for paste, I have to wait some seconds.

Used software:
- Mac OS X - 10.11.6 (El Capitan)
- ZSH v5.2
- oh-my-zsh - latest (installed today)

Benchmark (with plugins - see .zshrc - loaded):

> /usr/bin/time /usr/local/bin/zsh -i -c exit
>         4.63 real         0.47 user         0.29 sys

Benachmark (without plugins loaded):

> /usr/bin/time /usr/local/bin/zsh -i -c exit
>         1.38 real         0.24 user         0.13 sys

Here also my ".zshrc"-file:

``` zsh
# Path to your oh-my-zsh installation.
export ZSH=/Users/username/.oh-my-zsh

# Set name of the theme to load.
ZSH_THEME="agnoster"

# Which plugins would you like to load? (plugins can be found in ~/.oh-my-zsh/plugins/*)
plugins=(git command-not-found copydir copyfile cp history sublime vagrant composer symfony brew osx)

source $ZSH/oh-my-zsh.sh

# Set default-user to remove "user@hostname" from agnoster
DEFAULT_USER="username"

# Load zsh-syntax-highlighting
source /usr/local/share/zsh-syntax-highlighting/zsh-syntax-highlighting.zsh

# Set correct path for php-5.6
export PATH=/usr/local/php5-5.6.23-20160626-132038/bin:~/.composer/vendor/bin/:$PATH
```

Is this normal or can it be fixed?


---

*Resurrected by Resurrection Bot 🧬*
