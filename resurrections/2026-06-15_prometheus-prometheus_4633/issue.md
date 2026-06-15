# Monitoring kubernetes with prometheus from outside of k8s cluster.

**Repository:** [prometheus/prometheus](https://github.com/prometheus/prometheus)
**Issue:** [prometheus/prometheus#4633](https://github.com/prometheus/prometheus/issues/4633)
**Reactions:** 68 👍
**Created:** 2018-09-19T10:23:27Z
**Last Activity:** 2021-12-01T23:21:39Z
**Labels:** 

---

## Original Description

## Proposal
**The goal of this ticket is to understand how it would be possible or correct way to run prometheus outside of the k8s cluster being monitored. Or what kind of additonal development this would require.**

## Background
It is a common practice to not run the monitoring software on the stack that is being monitored.
It is important because during outages/problems with the cluster, prometheus might not be working or accessible, leaving the administrator in the blind while solving issues. 
Also the case of having multiple clusters to monitor, but wanting to have a centralized prometheus setup.

## Acceptable solutions
1) Prometheus configured against kubernetes API, similar manner as in kubectl works(provide host, client-certificate-data and client-key-data.
2) Run some sort of proxy inside of kubernetes cluster that takes care of tokens, discovery and accessing network inside of the cluster. So you configure central prometheus against this proxy, instead of kubernetes api and it provides the metrics from the cluster.
3) Provide instructions/documentation on how to use the current prometheus kubernetes_sd_configs opton to acheve the similar result

https://github.com/prometheus/prometheus/issues/2430 
In the end of it there are several users with this issue.

Having the kubernetes interanal network available on the monitoring server is not a desired solution because:
1) Multiple clusters might use the same IP ranges - so routing becomes complicated.
2) The monitoring server can be in another location or "zone" - so it might create latency issues for the entire network (depending on the solution used).



---

*Resurrected by Resurrection Bot 🧬*
