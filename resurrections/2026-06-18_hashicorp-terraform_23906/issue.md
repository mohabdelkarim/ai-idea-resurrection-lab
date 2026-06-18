# Request: Enable simple/native way to read .env files

**Repository:** [hashicorp/terraform](https://github.com/hashicorp/terraform)
**Issue:** [hashicorp/terraform#23906](https://github.com/hashicorp/terraform/issues/23906)
**Reactions:** 54 👍
**Created:** 2020-01-21T14:09:56Z
**Last Activity:** 2024-07-14T02:10:24Z
**Labels:** enhancement, config, functions

---

## Original Description


### Current Terraform Version
```
Terraform v0.12.19
```

### Use-cases
It's standard for code bases to have .env files, but I am not aware of any way to read their contents into terraform scripts.

### Attempted Solutions
There is the option for `terraform.tfvars`, but this requires my code base to maintain two secret-variable files (and their templates).

### Proposal
At minimum, instead of requiring that the `-var-file` flag take only files named exactly `terraform.tfvars`, terraform could be tweaked to allow for `.env` files to be specified. I'd also prefer to not have to also declare the variable name in the terraform script.




---

*Resurrected by Resurrection Bot 🧬*
