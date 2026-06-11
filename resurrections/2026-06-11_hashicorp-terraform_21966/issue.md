# `terraform show <plan>` "Backend reinitialization required" within subfolder

**Repository:** [hashicorp/terraform](https://github.com/hashicorp/terraform)
**Issue:** [hashicorp/terraform#21966](https://github.com/hashicorp/terraform/issues/21966)
**Reactions:** 72 👍
**Created:** 2019-07-03T18:42:26Z
**Last Activity:** 2023-04-23T02:13:04Z
**Labels:** enhancement, confirmed

---

## Original Description

**_NOTE: This ticket is when terraform is initialized above a subfolder_**

### Terraform Version
```
Terraform v0.12.3
+ provider.aws v2.17.0
```

### Terraform Configuration Files
```hcl
terraform {
  backend "local" {
  }
}
provider "aws" {
}
resource "aws_sns_topic" "test" {
    name = "test"
}
```

### Debug Output
N/A

### Crash Output
N/A

### Expected Behavior
The plan is show:
```bash
$ terraform show "test.plan"
  + aws_sns_topic.test
      id:     <computed>
      arn:    <computed>
      name:   "test"
      policy: <computed>
```
### Actual Behavior
Error stating that 

> Backend reinitialization required

### Steps to Reproduce
1. `terraform init ./subfolder-terraform`
```bash
$ terraform init ./subfolder-terraform

Initializing the backend...

Successfully configured the backend "local"! Terraform will automatically
use this backend unless the backend configuration changes.

Initializing provider plugins...
- Checking for available provider plugins...
- Downloading plugin for provider "aws" (terraform-providers/aws) 2.17.0...

The following providers do not have any version constraints in configuration,
so the latest version was installed.

To prevent automatic upgrades to new major versions that may contain breaking
changes, it is recommended to add version = "..." constraints to the
corresponding provider blocks in configuration, with the constraint strings
suggested below.

* provider.aws: version = "~> 2.17"

Terraform has been successfully initialized!

You may now begin working with Terraform. Try running "terraform plan" to see
any changes that are required for your infrastructure. All Terraform commands
should now work.

If you ever set or change modules or backend configuration for Terraform,
rerun this command to reinitialize your working directory. If you forget, other
commands will detect it and remind you to do so if necessary.
```

2. `terraform validate ./subfolder-terraform`
```bash
$ terraform validate ./subfolder-terraform`
Success! The configuration is valid.
```

3. `terraform plan -out=test.plan ./subfolder-terraform`
```bash
$ terraform plan -out=test.plan ./subfolder-terraform
Acquiring state lock. This may take a few moments...
Refreshing Terraform state in-memory prior to plan...
The refreshed state will be used to calculate this plan, but will not be
persisted to local or remote state storage.

------------------------------------------------------------------------

An execution plan has been generated and is shown below.
Resource actions are indicated with the following symbols:
  + create

Terraform will perform the following actions:

  # aws_sns_topic.test will be created
  + resource "aws_sns_topic" "test" {
      + arn    = (known after apply)
      + id     = (known after apply)
      + name   = "test"
      + policy = (known after apply)
    }

Plan: 1 to add, 0 to change, 0 to destroy.

--

---

*Resurrected by Resurrection Bot 🧬*
