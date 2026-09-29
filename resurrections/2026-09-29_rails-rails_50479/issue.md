# Add Thruster to Docker setup to get HTTP/2, X-Sendfile, Caching by default in Rails 8

**Repository:** [rails/rails](https://github.com/rails/rails)
**Issue:** [rails/rails#50479](https://github.com/rails/rails/issues/50479)
**Reactions:** 54 👍
**Created:** 2023-12-29T13:31:03Z
**Last Activity:** 2024-05-14T23:28:00Z
**Labels:** 

---

## Original Description

Puma does not support HTTP/2 out of the box, and there does not seem to be a short-term path to that changing. That means most people have to either stick nginx or a CDN in front of their app, which means more configuration and more moving parts.

As part of developing ONCE #1, we built a tiny, no-config Go-based proxy that sits in front of Puma to provide HTTP/2, public caching, and X-Sendfile setup. You run it by starting it with `airlock puma`, and that's it, you gain those speed upgrades without any hassle. This makes it a great fit for people who just want to run their Rails app off the default Dockerfile and with a minimum of fuss.

---

*Resurrected by Resurrection Bot 🧬*
