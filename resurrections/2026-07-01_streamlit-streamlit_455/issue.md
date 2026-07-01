# Ability to accept input from Charts, Tables, etc.

**Repository:** [streamlit/streamlit](https://github.com/streamlit/streamlit)
**Issue:** [streamlit/streamlit#455](https://github.com/streamlit/streamlit/issues/455)
**Reactions:** 283 👍
**Created:** 2019-10-18T06:39:20Z
**Last Activity:** 2024-09-15T12:49:05Z
**Labels:** type:enhancement, feature:st.dataframe, feature:charts, area:events

---

## Original Description

What if every output element could also serve as an input widget?

Then you could do things like:
* User clicks on chart datapoint → python script receives the value for that data point and does something with it
* User zooms into a chart → python script receives the new zoom bounds and does something with it
* User clicks on dataframe rows → python script receives row index and does something with it
* User click on two points on an image → python script draws a rectangle touching those points
* User edits a row on a dataframe → python script receives the new dataframe

Related discussions:
* https://discuss.streamlit.io/t/hover-and-click-events/586
* https://discuss.streamlit.io/t/setting-data-from-javascript/965/2

---

Community voting on feature requests enables the Streamlit team to understand which features are most important to our users.

**If you'd like the Streamlit team to prioritize this feature request, please use the 👍 (thumbs up emoji) reaction in response to the initial post.**

![Visits](https://hits.seeyoufarm.com/api/count/incr/badge.svg?url=https%3A%2F%2Fgithub.com%2Fstreamlit%2Fstreamlit%2Fissues%2F455&title=visits&edge_flat=false)


---

*Resurrected by Resurrection Bot 🧬*
