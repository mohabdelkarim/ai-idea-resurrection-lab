# kubectl run from a manifest file

**Repository:** [kubernetes/kubernetes](https://github.com/kubernetes/kubernetes)
**Issue:** [kubernetes/kubernetes#63214](https://github.com/kubernetes/kubernetes/issues/63214)
**Reactions:** 34 👍
**Created:** 2018-04-26T19:59:17Z
**Last Activity:** 2022-11-06T10:57:34Z
**Labels:** kind/feature, sig/cli, lifecycle/rotten

---

## Original Description

**Is this a BUG REPORT or FEATURE REQUEST?**:

/kind feature

**What happened**:

As discussed in #48684 we also have a use case where we would like to spin up a pod, run a command, and throw away the pod. `kubectl run` seems to support this except that it gets very complicated to bring up a pod matching the environment of an existing deployment. Specifically, attaching secrets.

The commonly cited example is to spin up a pod to run database migrations during a deployment.

That PR has to do with adding an `--end-from` option to the `kubectl run` but on further discussion, the use of `--override` seems to have resolved some of the problems. However, that has it's own issues, as [@javanthropus mentioned](https://github.com/kubernetes/kubernetes/pull/48684#issuecomment-382048645):

> This seems a little backwards logically though because we want the manifest to be the base definition, where the additional command line options provide overrides. It's also a mess to have to pass the entire manifest on the command line.

I would like to be able to specify the image on the command-line and override the spec. Specifically, I'd like to have a static manifest to load from and then add a tag to the image from our script so I can make sure I'm using the right image.

Something like this (which currently ignores the command-line:)

```
kubectl run -shell --image image:${TAG:-latest} --restart=Never --overrides $overrides -- bin/rails db:migrate
```

> Going further, as with the create and apply commands, it would be great if the manifest could be supplied in either JSON or YAML formats.

Agreed because all our other configuration files are in YAML.  I ended up with this so we could store the manifest in YAML like we do everything else:

```
--overrides $(ruby -r json -r yaml -e 'puts JSON.dump YAML.load_file("shell.yml")')
```

But I ran into further issues where if `--restart=Never` is on the `run` command, it launches a Pod, but _ignores_ the command line and just runs the default command in the Docker image.

**What you expected to happen**:

It would be great to have a `-f` option like `apply` does:

```
kubectl run -it --rm --restart=Never --filename pod.json
```

**Anything else we need to know?**:

**Environment**:
- Kubernetes version (use `kubectl version`):
  ```
  $ kubectl version
  Client Version: version.Info{Major:"1", Minor:"8", GitVersion:"v1.8.6", GitCommit:"6260bb08c46c31eea6cb538b34a9ceb3e406689c", GitTreeState:"clean", BuildDate:"2017-12-21T06:34:11Z", GoVersion:"go1.8.3", Compiler:"gc", Platform:"darwin/amd64"}
  Server Version: version.Info{Major:"1", Minor:"9+", GitVersion:"v1.9.6-gke.1", GitCommit:"cb151369f60073317da686a6ce7de36abe2bda8d", GitTreeState:"clean", BuildDate:"2018-04-07T22:06:59Z", GoVersion:"go1.9.3b4", Compiler:"gc", Platform:"linux/amd64"}
  ```


---

*Resurrected by Resurrection Bot 🧬*
