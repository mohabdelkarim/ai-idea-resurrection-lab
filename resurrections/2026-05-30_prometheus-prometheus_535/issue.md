# Add mechanism to perform bulk imports

**Repository:** [prometheus/prometheus](https://github.com/prometheus/prometheus)
**Issue:** [prometheus/prometheus#535](https://github.com/prometheus/prometheus/issues/535)
**Reactions:** 122 👍
**Created:** 2015-02-17T22:30:21Z
**Last Activity:** 2021-11-17T23:21:18Z
**Labels:** kind/enhancement, priority/P2, component/tsdb

---

## Original Description

Currently the only way to bulk-import data is a hacky one involving client-side timestamps and scrapes with multiple samples per time series. We should offer an API for bulk import. This relies on https://github.com/prometheus/prometheus/issues/481.

EDIT: It probably won't be an web-based API in Prometheus, but a command-line tool.

---

*Resurrected by Resurrection Bot 🧬*
