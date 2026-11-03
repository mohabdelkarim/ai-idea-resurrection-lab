# Port conflict with multiple "host:<port range>:port" services

**Repository:** [docker/compose](https://github.com/docker/compose)
**Issue:** [docker/compose#7188](https://github.com/docker/compose/issues/7188)
**Reactions:** 19 👍
**Created:** 2020-01-26T22:59:15Z
**Last Activity:** 2025-04-16T00:16:13Z
**Labels:** kind/bug, stale

---

## Original Description

<!--
Welcome to the docker-compose issue tracker! Before creating an issue, please heed the following:

1. This tracker should only be used to report bugs and request features / enhancements to docker-compose
    - For questions and general support, use https://forums.docker.com
    - For documentation issues, use https://github.com/docker/docker.github.io
    - For issues with the `docker stack` commands and the version 3 of the Compose file, use
      https://github.com/docker/cli
2. Use the search function before creating a new issue. Duplicates will be closed and directed to
   the original discussion.
3. When making a bug report, make sure you provide all required information. The easier it is for
   maintainers to reproduce, the faster it'll be fixed.
-->

## Description of the issue

If a compose file defines multiple services that share an overlapping port range, a port conflict occurs when `docker-compose up` is executed. This behavior started to happen for me when upgrading to Docker Desktop 2.2.0 (Stable) for Mac. The version I was previously running (I believe 2.1.5) was able to select distinct ports for the two services without conflicting. Here is a POC Docker Compose file:

```
version: '2.1'
services:
  postgres-foo:
    image: postgres
    ports:
      - "127.0.0.1:32768-61000:5432"

  postgres-bar:
    image: postgres
    ports:
      - "127.0.0.1:32768-61000:5432"
```

## Context information (for bug reports)

**Output of `docker-compose version`**

```
docker-compose version 1.25.2, build 698e2846
docker-py version: 4.1.0
CPython version: 3.7.5
OpenSSL version: OpenSSL 1.1.1d  10 Sep 2019
```

**Output of `docker version`**
```
Client: Docker Engine - Community
 Version:           19.03.5
 API version:       1.40
 Go version:        go1.12.12
 Git commit:        633a0ea
 Built:             Wed Nov 13 07:22:34 2019
 OS/Arch:           darwin/amd64
 Experimental:      false

Server: Docker Engine - Community
 Engine:
  Version:          19.03.5
  API version:      1.40 (minimum version 1.12)
  Go version:       go1.12.12
  Git commit:       633a0ea
  Built:            Wed Nov 13 07:29:19 2019
  OS/Arch:          linux/amd64
  Experimental:     false
 containerd:
  Version:          v1.2.10
  GitCommit:        b34a5c8af56e510852c35414db4c1f4fa6172339
 runc:
  Version:          1.0.0-rc8+dev
  GitCommit:        3e425f80a8c931f88e6d94a8c831b9d5aa481657
 docker-init:
  Version:          0.18.0
  GitCommit:        fec3683
```

**Output of `docker-compose config`**
(Make sure to add the relevant `-f` and other flags)
```
services:
  postgres-bar:
    image: postgres
    ports:
    - 127.0.0.1:32768-61000:5432/tcp
  postgres-foo:
    image: postgres
    ports:
    - 127.0.0.1:32768-61000:5432/tcp
version: '2.1'
```


## Steps to reproduce the issue

1. `docker-compose up`

### Observed result

Services fail to start and a port conflict error

---

*Resurrected by Resurrection Bot 🧬*
