# Proposal: support for args_file

**Repository:** [docker/compose](https://github.com/docker/compose)
**Issue:** [docker/compose#2545](https://github.com/docker/compose/issues/2545)
**Reactions:** 26 👍
**Created:** 2015-12-14T09:14:44Z
**Last Activity:** 2023-05-09T14:45:29Z
**Labels:** kind/feature

---

## Original Description

#### Motivation for this proposal
- build args have been introduced in Docker 1.9.0.
- #2163 proposes a new `build:` section in your Compose service
- builds args can be used to provide secret tokens (ssh key to clone a repository, github token...) during the build phase. These tokens should however not appear in your `docker-compose.yml` file but rather in a separate file.
#### Proposal

Introduce a `args_file:` section working the same way that `env_file:` works - but in the build phase.
#### Proposed documentation
##### args_file

Add build arguments from a file. Can be a single value or a list.

If you have specified a Compose file with `docker-compose -f FILE`, paths in `args_file` are relative to the directory that file is in.

Environment variables specified in `args` override these values.

``` yaml
build:
 args_file: .args

build:
  args_file:
    - ./common.env
    - ./apps/web.env
    - /opt/secrets.env
```

Compose expects each line in an env file to be in `VAR=VAL` format. Lines beginning with `#` (i.e. comments) are ignored, as are blank lines.

``` ini
# Set the secret token necessary to clone the dependencies
SECRET_TOKEN=yNxbjX
```


---

*Resurrected by Resurrection Bot 🧬*
