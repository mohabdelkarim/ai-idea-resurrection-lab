# Intermediate variables (OR: add interpolation support to input variables)

**Repository:** [hashicorp/terraform](https://github.com/hashicorp/terraform)
**Issue:** [hashicorp/terraform#4084](https://github.com/hashicorp/terraform/issues/4084)
**Reactions:** 122 👍
**Created:** 2015-11-27T02:15:15Z
**Last Activity:** 2017-08-21T22:33:45Z
**Labels:** enhancement, config

---

## Original Description

Not quite sure how to express this properly.

Input variables today cannot contain interpolations referring to other variables. I find myself bumping up against this now and then where I'd prefer to define a "default" value for an input variable based upon a composition of another input variable and some fixed string. 

If we could interpolate values inside default properties of input variables OR, terraform supported some kind of internal transitive intermediate variable which only exists in order to act as a binding point between inputs and other interpolation expressions I could accomplish what I want without having a lot of redundancy in inputs.

Slightly related, but I also long for the ability to reference the input values of a module (not just the outputs) because this is often where I tend to create such bindings. Of course, I can propagate the input to the module all the way through the module and emit as an output but that gets quite repetitive and clunky after a while.


---

*Resurrected by Resurrection Bot 🧬*
