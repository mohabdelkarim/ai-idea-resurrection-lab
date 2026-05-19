# Proposal for improving rate/increase 

**Repository:** [prometheus/prometheus](https://github.com/prometheus/prometheus)
**Issue:** [prometheus/prometheus#3806](https://github.com/prometheus/prometheus/issues/3806)
**Reactions:** 125 👍
**Created:** 2018-02-06T23:43:05Z
**Last Activity:** 2026-03-24T23:23:53Z
**Labels:** component/promql

---

## Original Description

I'm creating a separate, hopefully more focused (and civil) issue in an attempt to start a discussion on the problems (as seen by me and a number of others) with and possible solutions for `rate()` and `increase()`.

First, let me start by acknowledging that considering Prometheus' self-imposed constraints -- in particular having `foo[5m]` in the context of `rate(foo[5m])` only produce the data points that are strictly contained in the 5 minute range -- the current `rate()` and `increase()` implementations are essentially the most comprehensive solution for the particular problem.

That being said, I believe the core problems/limitations in the implementation stem from the constrained definition of what is a time range and an only slightly more generous definition (i.e. including the last point before the range) would provide a number of significant improvements. Why/how does including the last point before the range make any sense? Well, you could look at it as "the (rate of) increase between the value of the timeseries X minutes ago and now". And just as the current value of a timeseries is the last collected/evaluated point, so the value of the timeseries X seconds ago is the last collected/evaluated point at that time (i.e. the one immediately preceding the start of the range).

Or looking at it another way, if we consider a scrape interval of 1m (and, for now, no missed scrapes or series beginning/ending), a 5m rate calculated *"now"* should cover **the last 5m (plus jitter) starting from the last point collected**, just as the value of the timeseries *"now"* is **the last point collected**.

Moving on to the possible benefits of expanding the range to include the one extra point (in the past, not in the future):

1. Evaluating a rate/increase over the last X minutes every X minutes without any loss of data. Currently the options are either (a) compute a rate over significantly more than X minutes (which results in rates being averaged out over unnecessarily long ranges); or (b) compute the rate over `X minutes + scrape_interval`, which will basically give you the actual rate over X minutes, but requires you to be consistently aware of both the evaluation and scrape intervals.

2. `rate()` and `increase()` evaluations at the resolution of the underlying data, later aggregatable over arbitrarily long time ranges. Going back to the 1m scrape interval example, one would be able to compute a rate over 1m every minute, then, in a console/dashboard use `avg_over_time()` to obtain rates over any number of minutes/hours/days (and the same with `increase` and `sum_over_time`). Currently the rule of thumb is to calculate rates over 2.5-3.5x the scraping interval every 2 scraping intervals, resulting in (a) unnecessarily low resolution and (b) every resulting rate covering anywhere between 1 and 3 actual counter increases (2-4 points) with each increase arbitrarily included in either 1 or 2 rates. To be fair, the current implementation coul

---

*Resurrected by Resurrection Bot 🧬*
