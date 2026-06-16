# Have Fragments support dangerouslySetInnerHTML

**Repository:** [facebook/react](https://github.com/facebook/react)
**Issue:** [facebook/react#12014](https://github.com/facebook/react/issues/12014)
**Reactions:** 477 👍
**Created:** 2018-01-13T04:15:48Z
**Last Activity:** 2023-09-06T14:31:21Z
**Labels:** Type: Feature Request, Component: DOM

---

## Original Description

The addition of the `Fragment` in 16.2.0 is fantastic and helps keep our HTML semantic and clean. Unfortunately there is still no way to inject HTML without a wrapping tag.

```jsx
const HTML = <span>Hello World</span>;

<div key={ ID } dangerouslySetInnerHTML={ { __html: HTML } } />
```

which will render:

```html
<div><span>Hello World</span></div>
```

It would be mostly helpful for rendering HTML from jsx on the back end rather than in the SPA context. To me `Fragment` seems to be the ideal candidate to support `dangerouslySetInnerHTML` so that you may inject HTML without wrapping elements.

```jsx
const HTML = <span>Hello World</span>;

<Fragment key={ ID } dangerouslySetInnerHTML={ { __html: HTML } } />
```

would render:

```jsx
<span>Hello World</span>
```

Simple, obvious and aligned with the current API.

---

*Resurrected by Resurrection Bot 🧬*
