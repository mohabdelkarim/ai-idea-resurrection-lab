# Make React resilient to DOM mutations from Google Translate

**Repository:** [facebook/react](https://github.com/facebook/react)
**Issue:** [facebook/react#11538](https://github.com/facebook/react/issues/11538)
**Reactions:** 175 👍
**Created:** 2017-11-13T03:54:44Z
**Last Activity:** 2025-12-26T14:42:06Z
**Labels:** Type: Feature Request, Component: DOM

---

## Original Description

## Coming from search? See workaround here: https://github.com/facebook/react/issues/11538#issuecomment-417504600. And star this issue: https://bugs.chromium.org/p/chromium/issues/detail?id=872770.

**Do you want to request a *feature* or report a *bug*?**

Bug, though there's a decent chance it's a Chrome/Google Translate one

**What is the current behavior?**

When using Google Translate on a page using React 16, a certain code pattern produces a Javascript error (`Failed to execute 'removeChild' on 'Node': The node to be removed is not a child of this node.`) when the rendered content changes.

**If the current behavior is a bug, please provide the steps to reproduce and if possible a minimal demo of the problem via https://jsfiddle.net or similar (template for React 16: https://jsfiddle.net/Luktwrdm/, template for React 15: https://jsfiddle.net/hmbg7e9w/).**

(This has only been checked on macOS 10.13.1)
1. Navigate to https://qq49kwjynj.codesandbox.io/ in a Chrome browser set to some language other than Japanese.
2. Right click the page and select "Translate to English"
3. Click the checkbox, and the error will show.

The source of the example can be found at https://codesandbox.io/s/qq49kwjynj
The part of the code that seems to cause it is the following two lines:
```js
{this.state.checked && "選択済み"}
{!this.state.checked && "無選択"}
```
Changing this to the following fixes the behavior with Google Translate:
```js
{this.state.checked ? "選択済み" : "無選択"}
```

**What is the expected behavior?**

It should not produce an error.

**Which versions of React, and which browser / OS are affected by this issue? Did this work in previous versions of React?**

I created an identical example with React 15 at the following pages:
https://p93xxmr0rq.codesandbox.io/
https://codesandbox.io/s/p93xxmr0rq
When repeating the same steps outlined above, no error was produced.
It only seems to affect React 16.
As this is a Chrome-only feature, it only affects Chrome.

---

*Resurrected by Resurrection Bot 🧬*
