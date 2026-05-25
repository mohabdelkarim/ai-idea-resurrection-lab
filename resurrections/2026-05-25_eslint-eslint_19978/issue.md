# Change Request: Show a reminder when errors are suppressed

**Repository:** [eslint/eslint](https://github.com/eslint/eslint)
**Issue:** [eslint/eslint#19978](https://github.com/eslint/eslint/issues/19978)
**Reactions:** 7 👍
**Created:** 2025-08-02T00:32:28Z
**Last Activity:** 2025-10-04T22:32:09Z
**Labels:** enhancement, core, Stale

---

## Original Description

### ESLint version

v9.32.0

### What problem do you want to solve?

Currently, ESLint's [Bulk Suppressions](https://eslint.org/docs/latest/use/suppressions) mechanism completely hides suppressed errors and provides no indication that they exist. While this is useful for reducing noise, it also removes important context, especially in large codebases where tech debt is being suppressed temporarily.

Without any visible signal, developers can easily forget that suppressed errors exist, leading to:
- Long-term accumulation of silent issues
- Lack of visibility in IDEs or CI
- No easy way to prioritize cleanup or track tech debt

This invisibility makes it hard to balance short-term silence with long-term accountability.

### What do you think is the correct solution?

I'd like ESLint to optionally surface suppressed errors as reminders, such as:

> 💡 10 errors were suppressed in this file

This could appear as an "info" level diagnostic, ideally shown once per file, including metadata like the count of suppressed errors and possibly which rules were affected. 

If the behavior should be off by default to preserve the current silent suppression flow, maybe users could opt into it via a flag like `--remind-suppressions`. These reminders would be purely informational and wouldn't impact exit codes or `--max-warnings`.

The goal is to keep teams aware of lingering tech debt without reintroducing full error noise.

### Participation

- [ ] I am willing to submit a pull request for this change.

### Additional comments

- While possibly outside the scope of Suppressions, it would be useful to consider `CODEOWNERS` integration. In large repos, mapping suppressed errors to owning teams could improve triage and accountability.

- Related: https://github.com/eslint/eslint/issues/19706, which focuses on suppressing warnings. While that request aims to reduce noise, this one focuses on retaining visibility and tech debt awareness even when suppressions are in place.

---

*Resurrected by Resurrection Bot 🧬*
