# Support for right-aligned modules before line_break

**Repository:** [starship/starship](https://github.com/starship/starship)
**Issue:** [starship/starship#498](https://github.com/starship/starship/issues/498)
**Reactions:** 72 👍
**Created:** 2019-10-06T13:22:00Z
**Last Activity:** 2021-10-17T15:07:40Z
**Labels:** ✨ enhancement

---

## Original Description

## Feature Request

Some custom zsh prompts support right-aligning some elements. For example, my current zsh prompt looks like this (the time part is right-aligned on the first line):

![Screen Shot 2019-10-06 at 19 55 46](https://user-images.githubusercontent.com/198359/66269541-c83f8580-e873-11e9-8ea2-6afe031f8046.png)

Note that this is about right-aligning parts that come before the last line break. It is different from `RPROMPT`, which is for right-aligning an additional prompt on the same line as the input.

#### Is your feature request related to a problem? Please describe.
No.

#### Describe the solution you'd like
A new `alignment` option that affects a module's alignment.
A module is right-aligned if `alignment = "right"`, and there's a `line_break` module that comes after it in `prompt_order`.

#### Describe alternatives you've considered
1. Make `prompt_order` support a new structure other than a flat list.
2. Add a `right_align` module that changes layout direction until the next `line_break`. It's kind of like Unicode's right-to-left mark.


---

*Resurrected by Resurrection Bot 🧬*
