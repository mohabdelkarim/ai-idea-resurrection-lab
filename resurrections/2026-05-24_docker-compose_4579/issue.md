# Using scale number to adjust mounted volumes?

**Repository:** [docker/compose](https://github.com/docker/compose)
**Issue:** [docker/compose#4579](https://github.com/docker/compose/issues/4579)
**Reactions:** 38 👍
**Created:** 2017-03-06T22:57:51Z
**Last Activity:** 2025-03-04T16:11:49Z
**Labels:** kind/feature

---

## Original Description

I have a situation where I need to create many instances of a docker container, and they should have mounts that enable them to persist their data to different locations, so they aren't all running into each other. The containers are all worker agents for some non-docker-controlled server.

Essentially I need to be able to do something like this:
    
    services:
        agent:
            volumes:
                - /mnt/dat/agent_${DOCKER_SCALE_NUM}:/data/agent

I found a few references when googling around to something like this, but all of them seemed to have a resolution along the lines of "you don't really want to do this" or "here's some other way to solve your problem that doesn't involve doing this".

I doesn't need to be a sequential number or anything like that - I just need some way to get unique mount points for each one.

Is there an existing way to do this? If not, is anything planned?

Thanks!

---

*Resurrected by Resurrection Bot 🧬*
