# terraform get: can't use variable in module source parameter?

**Repository:** [hashicorp/terraform](https://github.com/hashicorp/terraform)
**Issue:** [hashicorp/terraform#1439](https://github.com/hashicorp/terraform/issues/1439)
**Reactions:** 67 👍
**Created:** 2015-04-09T08:15:28Z
**Last Activity:** 2019-07-24T01:51:51Z
**Labels:** enhancement, thinking, config

---

## Original Description

I'm trying to avoid hard-coding module sources; the simplest approach would be:

```
variable "foo_module_source" {
  default = "github.com/thisisme/terraform-foo-module"
}

module "foo" {
  source = "${var.foo_module_source}"
}
```

The result I get while attempting to run `terraform get -update` is

```
Error loading Terraform: Error downloading modules: error downloading module 'file:///home/thisisme/terraform-env/${var.foo_module_source}': source path error: stat /home/thisisme/terraform-env/${var.foo_module_source}: no such file or directory
```


---

*Resurrected by Resurrection Bot 🧬*
