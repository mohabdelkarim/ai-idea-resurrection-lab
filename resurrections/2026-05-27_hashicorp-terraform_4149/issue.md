# Partial/Progressive Configuration Changes

**Repository:** [hashicorp/terraform](https://github.com/hashicorp/terraform)
**Issue:** [hashicorp/terraform#4149](https://github.com/hashicorp/terraform/issues/4149)
**Reactions:** 298 👍
**Created:** 2015-12-02T23:54:12Z
**Last Activity:** 2022-04-26T22:03:45Z
**Labels:** enhancement, core, thinking, proposal, providers/protocol

---

## Original Description

For a while now I've been wringing my hands over the issue of using computed resource properties in parts of the Terraform config that are needed during the refresh and apply phases, where the values are likely to not be known yet.

The two primary situations that I and others have run into are:
- Interpolating into provider configuration blocks, as I described in #2976. This is allowed by Terraform but fails in unintuitive ways when a chicken-and-egg problem arises.
- Interpolating into the `count` modifier on resource blocks, as described in #1497. Currently this permits only variables, but having it configurable from resource attributes would be desirable.

After a number of false-starts trying to find a way to make this work better in Terraform, I believe I've found a design that builds on concepts already present in Terraform, and that makes only small changes to the Terraform workflow. I arrived at this solution by "paving the cowpaths" after watching my coworkers and I work around the issue in various ways.

---

The crux of the proposal is to alter Terraform's workflow to support the idea of _partial application_, allowing Terraform to apply a complicated configuration over several passes and converging on the desired configuration. So from the user's perspective, it would look something like this:

``` bash
$ terraform plan -out=tfplan
... (yada yada yada) ...

Terraform is not able to apply this configuration in a single step. The plan above
will partially apply the configuration, after which you should run "terraform plan"
again to plan the next set of changes to converge on the given configuration.

$ terraform apply tfplan
... (yada yada yada) ...

Terraform has only partially-applied the given configuration. To converge on
the final result, run "terraform plan" again to plan the next set of changes.

$ terraform plan -out=tfplan
... (yada yada yada) ...

$ terraform apply
... (yada yada yada) ...

Success! ....
```

For a particularly-complicated configuration there may be three or more apply/plan cycles, but eventually the configuration should converge.

`terraform apply` would also exit with a predictable exit status in the "partial success" case, so that Atlas can implement a smooth workflow where e.g. it could immediately plan the next step and repeat the sign-off/apply process as many times as necessary.

This workflow is intended to embrace the existing workaround of using the `-target` argument to force Terraform to apply only a subset of the config, but improve it by having Terraform itself detect the situation. Terraform can then calculate itself which resources to target to plan for the maximal subset of the graph that can be applied in a single action, rather than requiring the operator to figure this out.

By teaching Terraform to identify the problem and propose a solution itself, Terraform can guide new users through the application of trickier configurations, rather than requir

---

*Resurrected by Resurrection Bot 🧬*
