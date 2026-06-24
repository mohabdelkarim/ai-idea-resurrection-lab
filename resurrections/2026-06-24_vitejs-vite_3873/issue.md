# vite build --watch HMR

**Repository:** [vitejs/vite](https://github.com/vitejs/vite)
**Issue:** [vitejs/vite#3873](https://github.com/vitejs/vite/issues/3873)
**Reactions:** 54 👍
**Created:** 2021-06-19T23:35:24Z
**Last Activity:** 2023-08-05T00:23:28Z
**Labels:** enhancement: pending triage, p2-to-be-discussed

---

## Original Description

### Clear and concise description of the problem

My current setup involves using the `vite build --watch` command so that I am able to serve my Vite frontend from a custom webserver. It would be great if hot module reloading could be used in this configuration.

This feature is supported by [Snowpack](https://www.snowpack.dev) via the command `snowpack build --watch. --hmr`.

### Suggested solution

The HMR server could still be served on a port controlled by Vite and the HMR code could still be included in the outputted files. This way the HMR would work even though the frontend files were served with another webserver.

I am new to Vite's codebase but with some pointers about where to start would be happy to attempt a PR.

---

*Resurrected by Resurrection Bot 🧬*
