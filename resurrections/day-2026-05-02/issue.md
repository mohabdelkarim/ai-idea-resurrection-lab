# Feature request: Allow using lists and maps with conditionals

**Repository:** [hashicorp/terraform](https://github.com/hashicorp/terraform)
**Issue:** [hashicorp/terraform#12453](https://github.com/hashicorp/terraform/issues/12453)
**Reactions:** 177 👍
**Created:** 2017-03-05T23:38:44Z
**Last Activity:** 2019-07-24T01:51:39Z
**Labels:** enhancement, config

---

## Original Description

I found out today that if you try to use a list or a map with a conditional, you get the error:

```
* At column 3, line 1: conditional operator cannot be used with list values in:
```

It turns out this is an explicit check built into the [TypeCheck method](https://github.com/hashicorp/terraform/blob/1bae160796461066a07ca1721c4688db0d5ce567/vendor/github.com/hashicorp/hil/check_types.go#L426). 

The comment above the code says "for now this is simply prohibited because it doesn't seem to be a common enough case to be worth the complexity." I thought I'd toss out at least one use case where this would be handy:

* I'm creating a module that creates a number of resources, including an ELB. 
* One of the inputs to the module is a variable called `is_internal_elb`, which is used to set the `internal` parameter of the ELB to true for internal ELBs and false for public ELBs. 
* The ELB takes in a `subnets` parameter, which is a list of subnet IDs to attach to the ELB. When `is_internal_elb` is set to true, I'd like to set this to a list of private subnet IDs. When `is_internal_elb` is false, I'd like to set it to a list of public subnet IDs.

Rough pseudo code:

```hcl
resource "aws_elb" "elb" {
  name = "${var.elb_name}"
  internal = "${var.is_internal_elb}"

  subnets = ["${var.is_internal_elb ? var.private_subnet_ids : var.public_subnet_ids}"]
}
```

This seems like a fairly straightforward use case, but with the current `TypeCheck` method, it won't work.

---

*Resurrected by Resurrection Bot 🧬*
