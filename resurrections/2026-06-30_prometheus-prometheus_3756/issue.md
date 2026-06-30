# Support for multiple ports in annotations

**Repository:** [prometheus/prometheus](https://github.com/prometheus/prometheus)
**Issue:** [prometheus/prometheus#3756](https://github.com/prometheus/prometheus/issues/3756)
**Reactions:** 132 👍
**Created:** 2018-01-29T07:28:26Z
**Last Activity:** 2024-12-17T23:21:16Z
**Labels:** kind/enhancement, component/service discovery

---

## Original Description

The use case is if you have for example several containers in a pod, currently with the port annotation it seems you can only specify one port. The only way i see to scrape several ports is removing the port annotation, the problem is that ports that i dont wanna get scraped are scraped.


---

*Resurrected by Resurrection Bot 🧬*
