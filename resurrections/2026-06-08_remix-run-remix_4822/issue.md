# hydration error when there is a chrome extension that modifies DOM

**Repository:** [remix-run/remix](https://github.com/remix-run/remix)
**Issue:** [remix-run/remix#4822](https://github.com/remix-run/remix/issues/4822)
**Reactions:** 52 👍
**Created:** 2022-12-10T18:16:32Z
**Last Activity:** 2025-03-20T10:56:12Z
**Labels:** bug:unverified, external, hydration

---

## Original Description

### What version of Remix are you using?

latest

### Steps to Reproduce

I installed an extension that modifies DOM such as Grammar Checker into my browser and tried to develop a web app with Remix.
I get the following errors and the styles of the app were messed up.

Hydration failed because the initial UI does not match what was rendered on the server.
There was an error while hydrating. Because the error happened outside of a Suspense boundary, the entire root will switch to client rendering.

### Expected Behavior

I have errors when I install any extension that modifies DOM into my browser 

### Actual Behavior

The favicon and styles are messed up
The important thing is that this error has already been mentioned many times and there is no exact solution
What's even more interesting is that the https://remix.run site doesn't have this error occur even if it was developed with Remix

---

*Resurrected by Resurrection Bot 🧬*
