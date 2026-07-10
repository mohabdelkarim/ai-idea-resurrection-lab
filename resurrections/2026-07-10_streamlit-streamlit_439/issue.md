# Support custom HTTP requests

**Repository:** [streamlit/streamlit](https://github.com/streamlit/streamlit)
**Issue:** [streamlit/streamlit#439](https://github.com/streamlit/streamlit/issues/439)
**Reactions:** 265 👍
**Created:** 2019-10-17T04:21:37Z
**Last Activity:** 2026-04-10T09:26:12Z
**Labels:** type:enhancement, area:utilities

---

## Original Description

See: https://discuss.streamlit.io/t/streamlit-restful-app/409

Some users would like to have their Streamlit servers work double duty as both a Streamlit app server and a data server (for REST endpoints, for example)

### API proposal 1

A traditional-looking API for that would be something like:
```python
st.server.add_route('foo', foo_callback)
```

Then, when a POST or GET HTTP request is made against `/foo`, the callback `foo_callback` would handle it and return a response.

I haven't thought through whether this would be possible to implement given our current "run from the top" architecture. It's possible this would require a big refactor.

### API proposal 2

A more Streamlit-style API would be something like:

```python
if st.server.request.foo == 'bar':
  st.server.respond({'data': df})
  # And .respond() would cause the script to finish executing immediately.
```

In this proposal, the `if` condition would be true if:
- The user sent a POST to `/` with `foo` set to `bar` (either in a form or in JSON)
- Or the user sent a GET to `/?foo=bar`

This API is easier to implement and arguably easier to understand.

---
My preference at this point is proposal 2.

That said, both of these proposals are just straw-man designs to start a discussion. I believe neither of these is ready to implement at this point.

---

Community voting on feature requests enables the Streamlit team to understand which features are most important to our users.

**If you'd like the Streamlit team to prioritize this feature request, please use the 👍 (thumbs up emoji) reaction in response to the initial post.**

![Views](https://api.views-badge.org/badge/st-issue-439)


---

*Resurrected by Resurrection Bot 🧬*
