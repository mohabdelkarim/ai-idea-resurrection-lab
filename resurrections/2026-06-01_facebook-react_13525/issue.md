# React Fire: Modernizing React DOM

**Repository:** [facebook/react](https://github.com/facebook/react)
**Issue:** [facebook/react#13525](https://github.com/facebook/react/issues/13525)
**Reactions:** 2389 👍
**Created:** 2018-08-31T19:45:53Z
**Last Activity:** 2022-09-23T12:27:56Z
**Labels:** Component: DOM, Type: Big Picture, React Core Team

---

## Original Description


-------------

**For latest status, see an update from June 5th, 2019: https://github.com/facebook/react/issues/13525#issuecomment-499196939**

-------------

This year, the React team has mostly been focused on [fundamental improvements to React](https://reactjs.org/blog/2018/03/01/sneak-peek-beyond-react-16.html).

As this work is getting closer to completion, we're starting to think of what the next major releases of React DOM should look like. There are quite a few [known problems](https://github.com/facebook/react/issues?q=is%3Aopen+is%3Aissue+label%3A%22Type%3A+Bug%22+label%3A%22Component%3A+DOM%22), and some of them are hard or impossible to fix without bigger internal changes.

We want to undo past mistakes that caused countless follow-up fixes and created much technical debt. We also want to remove some of the abstraction in the event system which has been virtually untouched since the first days of React, and is a source of much complexity and bundle size.

We're calling this effort "React Fire".

### 🔥 React Fire 

**React Fire** is an effort to modernize React DOM. Our goal is to make React better aligned with how the DOM works, revisit some controversial past decisions that led to problems, and make React smaller and faster.

We want to ship this set of changes in a future React major release because some of them will unfortunately be breaking. Nevertheless, we think they're worth it. And we have more than 50 thousands components at Facebook to keep us honest about our migration strategy. We can't afford to rewrite product code except a few targeted fixes or automated codemods. 

### Strategy

There are a few different things that make up our current plan. We might add or remove something but here's the thinking so far:

* **Stop reflecting input values in the `value` attribute (https://github.com/facebook/react/issues/11896).** This was originally added in React 15.2.0 via https://github.com/facebook/react/pull/6406. It was very commonly requested because people's conceptual model of the DOM is that the `value` they see in the DOM inspector should match the `value` JSX attribute. But that's not how the DOM works. When you type into a field, the browser doesn't update the `value` attribute. React shouldn't do it either. It turned out that this change, while probably helpful for some code relying on CSS selectors, caused a cascade of bugs — some of them still unfixed to this day. Some of the fallout from this change includes: https://github.com/facebook/react/issues/7179, https://github.com/facebook/react/issues/8395, https://github.com/facebook/react/issues/7328, https://github.com/facebook/react/issues/7233, https://github.com/facebook/react/issues/11881, https://github.com/facebook/react/issues/7253, https://github.com/facebook/react/pull/9584, https://github.com/facebook/react/pull/9806, https://github.com/facebook/react/pull/9714, https://github.com/facebook/react/pull/11534, https://github.com/facebook/

---

*Resurrected by Resurrection Bot 🧬*
