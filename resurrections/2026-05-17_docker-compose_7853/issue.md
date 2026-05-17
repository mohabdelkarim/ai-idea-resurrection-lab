# Please expose current user and group ID as new variables for use inside docker-compose.yml

**Repository:** [docker/compose](https://github.com/docker/compose)
**Issue:** [docker/compose#7853](https://github.com/docker/compose/issues/7853)
**Reactions:** 59 👍
**Created:** 2020-10-07T17:49:29Z
**Last Activity:** 2025-11-07T08:34:04Z
**Labels:** kind/feature

---

## Original Description

**Is your feature request related to a problem? Please describe.**
Hi, docker-compose rocks, keep up the good work! :pray: 
I had cases where the container should be running with the same user and group ID as the docker-compose process, e.g. so that files created inside the container will start out with the right owner without any need for initial root permissions (which is not cool for security) or `chown`'ing files et cetera.

As of today, inside `docker-compose.yml` a service definition can already ask for a specific user by means of syntax `user: "<user_id>:<group_id>"` but there are no predefined variables to effectively achieve something *like* `user: "$(id -u):$(id -g)"` from inside the YAML file with convenice. The list of [Compose file and CLI variables](https://docs.docker.com/compose/env-file/#compose-file-and-cli-variables) does not document any variables like that.

Here's a few documented examples for other people trying to achieve the same, and they all need to resort to means *outside* the `docker-compose.yml` file: [[1]](https://stackoverflow.com/questions/55916455/export-current-user-id-in-makefile-for-docker-compose) [[2]](https://medium.com/faun/set-current-host-user-for-docker-container-4e521cef9ffc#b470) [[3]](https://jtreminio.com/blog/running-docker-containers-as-current-host-user/) [[4]](https://gist.github.com/prog/48341108404cae266d72ed4a470c1bc3) [[5]](https://stackoverflow.com/questions/56844746/how-to-set-uid-and-gid-in-docker-compose/56844765) [[6]](https://dev.to/acro5piano/specifying-user-and-group-in-docker-i2e).

**Describe the solution you'd like**
It would be great to have two more predefined variables:
- `COMPOSE_USER_ID` predefined with the effective user ID, as return by `$(id -u)`
- `COMPOSE_GROUP_ID` predefined with the effective group ID, as return by `$(id -g)`

With those two variables, a docker-compose.yml file could now use syntax `user: "${COMPOSE_USER_ID?}:${COMPOSE_GROUP_ID?}"` to conveniently have a container running as the same user as the one calling docker-compose. Wouldn't that be nice! :smiley: 

Feature request #3849 seems to be rooted in a similar need, but my impression was that the door to arbitrary code execution has been kept shut for security reasons so far and adding two variables should work without questioning the current threat model.

**Describe alternatives you've considered**
You could define `COMPOSE_USER_ID` and `COMPOSE_GROUP_ID` *outside* of `docker-compose.yml` e.g.
```
COMPOSE_USER_ID="$(id -u)" COMPOSE_GROUP_ID="$(id -g)" docker-compose run ...
```
but it's not very convenient, does not work out of the box, and it's not standardized.

**Additional context**
```console
# cat docker-compose.yml 
version: "3"

services:
  debian:
    image: debian:sid
    user: "${COMPOSE_USER_ID?}:${COMPOSE_GROUP_ID?}"

# COMPOSE_USER_ID="$(id -u)" COMPOSE_GROUP_ID="$(id -g)" docker-compose run debian sh -c id  # unpatched
Creating tmpyvecgpc8mx_debian_ru

---

*Resurrected by Resurrection Bot 🧬*
