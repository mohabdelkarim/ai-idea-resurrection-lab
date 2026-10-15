# Prometheus docker container shouldn't run as user nobody

**Repository:** [prometheus/prometheus](https://github.com/prometheus/prometheus)
**Issue:** [prometheus/prometheus#3441](https://github.com/prometheus/prometheus/issues/3441)
**Reactions:** 53 👍
**Created:** 2017-11-08T19:41:11Z
**Last Activity:** 2025-09-03T23:21:02Z
**Labels:** priority/Pmaybe

---

## Original Description

With the update to 2.0, the Docker container was modified so that Prometheus runs as the user "nobody" (UID/GID 99/99) (#2859). While it's good that Prometheus is no longer running as root, it's not the best idea either to run as "nobody". There are many examples of Docker containers out there that allow changing the UID/GID at runtime that could be borrowed from. At a minimum a different static UID/GID should be used.


---

*Resurrected by Resurrection Bot 🧬*
