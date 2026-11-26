# Store metrics docstrings and allow to query them

**Repository:** [prometheus/prometheus](https://github.com/prometheus/prometheus)
**Issue:** [prometheus/prometheus#2747](https://github.com/prometheus/prometheus/issues/2747)
**Reactions:** 23 👍
**Created:** 2017-05-19T16:02:55Z
**Last Activity:** 2019-03-22T15:09:44Z
**Labels:** help wanted, kind/enhancement, component/ui, not-as-easy-as-it-looks, priority/P3

---

## Original Description

Prometheus doesn't currently store metrics docstrings (`#HELP` lines in text format). They could be useful for a user in various UIs and dashboards.

I think they can be stored as simple non-versioned metainformation. If some metric has different docstrings in various jobs, then log a warning and overwrite it (the last write wins).

Obviously, they also should be exposed via API.

---

*Resurrected by Resurrection Bot 🧬*
