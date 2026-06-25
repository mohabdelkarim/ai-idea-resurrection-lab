# [Feature request] Email templating in Alert engine

**Repository:** [grafana/grafana](https://github.com/grafana/grafana)
**Issue:** [grafana/grafana#7121](https://github.com/grafana/grafana/issues/7121)
**Reactions:** 92 👍
**Created:** 2017-01-03T16:08:29Z
**Last Activity:** 2024-05-27T01:49:02Z
**Labels:** type/feature-request, area/alerting, area/alerting/notifications, stale

---

## Original Description

**- What Grafana version are you using?**
4.0.1
**- What datasource are you using?**
OpenTSDB
**- What OS are you running grafana on?**
CentOS 7.2


I would like to congratulate for including alerting feature in Grafana 4, this is just what I needed to create alerts for things that our monitoring did not cover. To make email alerting more flexible I would propose to create simple mail templating engine:

**Current Use Case**
We setup alert thresholds and alert recipient as well as static text which informs about the cause, incomplete Graph (no text, no legend) is also added

**What is missing?**
However I think that the email engine lacks templating option (or documentation on this feature if it is possible). What I would like to request is:
- formatting the metric value with units or just manipulate it via variable
- ability to use some HTML tags / BB code / custom grafana rules for text formatting (at least support for generating links)
- use of dasboard-specific variables such as query alias, graph title, dashboard title or template variables defined in dashboard (could be used as a temporary workaround since alerts do not work with template vars in queries), date of alert triggering - this is mainly for customizing links which Grafana could generate when alert occurs
- Create PNG from the graph state when alert triggered - currently no text is drawn onto the graph making it quite unreadable - exact PNG image from configured view would have been sufficient if possible
- Subject templating - simple textbox with variable support

Pros:
- make alerts customizable, lazy users will not be forced to create new mail filters
- make messages clear to understand - at least by formatting it to the unit used in graph - for instance in rates measured in byte difference but displayed in Mbit/s

Cons:
- can't think of any, except somebody has to write some code and docs on it

Keep up the good work !



---

*Resurrected by Resurrection Bot 🧬*
