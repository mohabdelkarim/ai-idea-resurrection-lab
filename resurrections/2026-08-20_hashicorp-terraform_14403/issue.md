# Tainted `null_resource` with `destroy provisioner` does not run the destroy command.

**Repository:** [hashicorp/terraform](https://github.com/hashicorp/terraform)
**Issue:** [hashicorp/terraform#14403](https://github.com/hashicorp/terraform/issues/14403)
**Reactions:** 83 👍
**Created:** 2017-05-11T16:48:56Z
**Last Activity:** 2022-10-28T02:39:32Z
**Labels:** bug, provisioner/local-exec

---

## Original Description

Hi there,

I am using `destroy` provisioner on `null_resource`, this works great on `terraform destroy`. When I try to taint this resource and re-apply, the destroy script does not run. Is this expected?

### Terraform Version
Terraform v0.9.5

### Affected Resource(s)
- null_resource

### Terraform Configuration Files
```json
{
  "provider": {
    "azurerm": {
      "client_id": "${var.client_id}",
      "client_secret": "${var.client_secret}",
      "subscription_id": "${var.subscription_id}",
      "tenant_id": "${var.tenant_id}"
    }
  },
  "resource": {
    "null_resource": {
      "test2_add_group_role": {
        "provisioner": [
          {
            "local-exec": {
              "command": "\naz ad group create --display-name dev-group --mail-nickname dev-group\n\n"
            }
          },
          {
            "local-exec": {
              "command": "\naz ad group delete -g dev-group\n\n",
              "on_failure": "continue",
              "when": "destroy"
            }
          }
        ]
      }
    }
  }
}
```
### Expected Behavior
The `destroy` provisioner should run when the resource is tainted, and re-applied.

### Actual Behavior
The `destroy` provisioner did not run.

### Steps to Reproduce
1. `terraform taint null_resource.test2_add_group_role`
2. `terraform plan`
3. `terraform apply`


---

*Resurrected by Resurrection Bot 🧬*
