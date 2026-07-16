# Document memory planning guidelines

**Repository:** [prometheus/prometheus](https://github.com/prometheus/prometheus)
**Issue:** [prometheus/prometheus#5469](https://github.com/prometheus/prometheus/issues/5469)
**Reactions:** 59 👍
**Created:** 2019-04-16T18:51:39Z
**Last Activity:** 2024-09-15T23:21:12Z
**Labels:** help wanted, priority/P3, component/documentation

---

## Original Description

## Proposal
I would like to ask the prometheus dev community to consider adding some documentation around estimating the memory requirements of prometheus.  
The fact that prometheus is mostly being run in memory capped containers and is OOMkilled when reaching the mem limit is surprising many users who are accustomed to robust software that degrades instead of dying.

I've been running prometheus in production for a while which is occasionally OOMKilled. I have expanded the memory limits more than once to arbitrary limits but I would prefer to make an educated estimation for a reasonable limit given my workload.  
I have read the TSDB design paper which was super interesting but I don't feel that it gave me a practical hint to my problem, and even if I did, I think this is something the average user is far away from doing, and I'd consider this a development task rather then a usage question.  
Since being in this state I have also learned that many others are in the same situation and are just "living with it", which is unfortunate.

Can we please discuss this topic, and possibly document our conclusions in the readme?
(I understand that planning for queries is harder, so we can stick to planning for metrics ingestion only which is supposed to be predictable)

---

*Resurrected by Resurrection Bot 🧬*
