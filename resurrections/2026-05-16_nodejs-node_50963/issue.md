# enable corepack by default

**Repository:** [nodejs/node](https://github.com/nodejs/node)
**Issue:** [nodejs/node#50963](https://github.com/nodejs/node/issues/50963)
**Reactions:** 271 👍
**Created:** 2023-11-29T11:01:40Z
**Last Activity:** 2025-03-23T21:17:51Z
**Labels:** feature request

---

## Original Description

### What is the problem this feature will solve?

we try to use corepack and "packageManager" to force developers use the same pnpm version, but developers always forget to enable corepack(because it's turned off by default and when we switch node version it's turned off again) which makes packageManager not working at all

### What is the feature you are proposing to solve the problem?

enable corepack by default if package.json contains "packageManager".

### What alternatives have you considered?

we currently use "engine.pnpm" field to check whether developers use same pnpm version but engine field is annoying when we deals with tons of projects with different version

---

*Resurrected by Resurrection Bot 🧬*
