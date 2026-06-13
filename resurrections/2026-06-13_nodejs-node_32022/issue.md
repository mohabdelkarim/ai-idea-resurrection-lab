# Solid Node.js with official type system support

**Repository:** [nodejs/node](https://github.com/nodejs/node)
**Issue:** [nodejs/node#32022](https://github.com/nodejs/node/issues/32022)
**Reactions:** 27 👍
**Created:** 2020-02-29T10:21:05Z
**Last Activity:** 2023-05-05T01:26:53Z
**Labels:** feature request, stale

---

## Original Description

## Is your feature request related to a problem? Please describe.

While js became more and more popular, typescript and flow appears to deal with  stability and maintainability for large projects, yet we lack support for type definitions for Node.js core api. I think the needs goes strong and strong, one proof is that https://www.npmjs.com/package/@types/node has reached 23 million download weekly.

Community already has `@type/node`, should we really support it in core ?
I think we should, here are the reasons:

### It's not reflect the api change quickly enough
For example, the `wasi` api takes some time added to the repo.
Apis like newly or changed takes time to get adopted, developers will has
to wait for this.

### It's not related to Node.js version consistently
this package doesn't related Node.js versions. But we has lts, latest and other versions, this can be problematic and got surprised behavior. If we have 
official support, developers can choose the related version and got precise result.

### other
It's only for typescript. We can expand our official type system to flow or other newly solutions.
Also contribute to this package is too much pain.

## Describe the solution you'd like

I am thinking we generate types file from our markdown doc or js source file (the `libs` folder ), not sure whether this eventually can work. Another solution is we invent a new dsl :)

Eventually we should make should publish types package when we release a new Node.js version.





---

*Resurrected by Resurrection Bot 🧬*
