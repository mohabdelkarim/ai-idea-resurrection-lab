# Rule Proposal: prefer-optional-chaining

**Repository:** [eslint/eslint](https://github.com/eslint/eslint)
**Issue:** [eslint/eslint#13430](https://github.com/eslint/eslint/issues/13430)
**Reactions:** 77 👍
**Created:** 2020-06-21T04:36:38Z
**Last Activity:** 2025-06-05T15:36:08Z
**Labels:** rule, accepted, feature

---

## Original Description

**Please describe what the rule should do:**

The new rule warns `obj && obj.prop`-like notations to suggest `obj?.prop`.

**What new ECMAScript feature does this rule relate to?**

Optional chaining

**What category of rule is this? (place an "X" next to just one item)**

[X] Suggests an alternate way of doing something (suggestion)

**Provide 2-3 code examples that this rule will warn about:**

<!-- Put your code examples here -->
```js
//✖ BAD
obj && obj.prop
obj != null ? obj.prop : undefined
obj && obj[key]
obj != null ? obj[key] : undefined
func && func()
func != null ? func() : undefined
if (func) func()
if (func) { func() }

//✔ GOOD
obj?.prop
obj?.[key]
func?.()
```

**Why should this rule be included in ESLint (instead of a plugin)?**

`obj && obj.prop`-like notation is a popular practice. This rule will help people to learn the new syntax Optional Chaining. This is about a language feature rather than third-party platforms or libraries.

**Are you willing to submit a pull request to implement this rule?**

Yes.


---

*Resurrected by Resurrection Bot 🧬*
