# rate()/increase() extrapolation considered harmful

**Repository:** [prometheus/prometheus](https://github.com/prometheus/prometheus)
**Issue:** [prometheus/prometheus#3746](https://github.com/prometheus/prometheus/issues/3746)
**Reactions:** 50 👍
**Created:** 2018-01-26T15:42:50Z
**Last Activity:** 2019-11-25T11:19:32Z
**Labels:** 

---

## Original Description

**The problem**

*[Feel free to skip ahead to the proposed solution, as I'm guessing the problem is widely understood. Or just read the last couple of paragraphs for a real-life example of the problem and my current workaround.]*

I've been trying to deal with the errors introduced by the `rate()` and `increase()` functions for so long that I keep going back every few months and spend a couple of hours tweaking Grafana dashboards before I remember that there is literally **no way of getting an accurate result** out of them short of using recorded rules for everything and, even in that case, working around and against Prometheus.

To clarify, let's assume I have a monitoring configuration with **scrapes every 5 seconds** and **rule evaluation every 10 seconds**. It collects among other things a `request_count` counter, that increases by 1 every 20 seconds. Let's also assume that I would really like a Grafana graph that displays an accurate number of requests over time, on a dashboard with an adjustable time range. (I.e. I want to be able to look at 15 minutes, 1 hour and 7 days on the same dashboard, with Grafana automatically adjusting the resolution.) Not a tall order, right?

For the purpose of clarity, here is how the `request_count` samples would look like (at a 5 second resolution):

    [0, 1, 1, 1, 1, 2, 2, 2, 2, 3, 3, 3, 3, 4, 4, 4, 4, ...]

The naive approach is you add a graph and put in an expression along the lines of:

    increase(request_count[$__interval])

and set *Min step* to `10s` (I would prefer a *Min step* of `5s`, since the resolution of the underlying data is 5 seconds, but let's not even go there yet). Ideally the graphed values (with a 10 second resolution) would look something like:

    [0, 1, 0, 1, 0, 1, 0, 1, 0, ...]

What I'm getting instead, depending on the exact time I reload the page is one of:

    [0, 2, 0, 2, 0, 2, 0, 2, 0, ...]

or

    [0, 0, 0, 0, 0, 0, 0, 0, 0, ...]

This is because what `increase()` ends up doing is it calculates the increase between disjoint pairs of values (i.e. `(v0, v1)`, `(v2, v3)`, `(v4, v5)`), losing half of the data in the process, and extrapolates it to 10 seconds, ending up with double the actual increase. At 15 seconds resolution it only throws away a third of the data and the increases it doesn't throw away get multiplied by 1.5 due to the extrapolation. As the resolution decreases, less data gets thrown away and the multiplier gets closer to 1 but there is, as I said before, literally no way to get an accurate `rate()`/`increase()` value in a range query directly from a counter. `rate()` is not affected by the multiplier issue, but still suffers from thrown away data and noise.

Even with less discrete data, such as CPU usage, the graph jumps every 5 seconds between one shape and another. In particular, if I'm looking at Prometheus' own CPU usage, because my rule evaluation happens every 10 seconds but takes less than 5 seconds, the graph keeps

---

*Resurrected by Resurrection Bot 🧬*
