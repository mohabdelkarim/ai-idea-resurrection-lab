# Setting container hostname to `service_name-xx` instead of container-id

**Repository:** [docker/compose](https://github.com/docker/compose)
**Issue:** [docker/compose#9858](https://github.com/docker/compose/issues/9858)
**Reactions:** 44 👍
**Created:** 2022-09-19T04:03:57Z
**Last Activity:** 2025-04-29T18:41:02Z
**Labels:** kind/feature

---

## Original Description

For this sample compose file
```yaml
services:
  my-app:
    image: my-image:0.1

  his-app:
    image: his-image:0.1
```

Compose creates my-app-1 container for my-app with host-name as container-id say `rndmcntrid`

This container is reachable from other services like `his-app-1` with `my-app`, `my-app-1` or `rndmcntrid`.

Can we have compose set container hostname as `service-1`? e.g. in case of my-app above, hostname be set to `my-app-1` instead of `rndmcntrid`
```
Docker Compose version v2.10.2
```

---

*Resurrected by Resurrection Bot 🧬*
