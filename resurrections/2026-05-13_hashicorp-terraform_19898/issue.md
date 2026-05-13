# Optional arguments in object variable type definition

**Repository:** [hashicorp/terraform](https://github.com/hashicorp/terraform)
**Issue:** [hashicorp/terraform#19898](https://github.com/hashicorp/terraform/issues/19898)
**Reactions:** 1757 👍
**Created:** 2018-12-30T10:37:06Z
**Last Activity:** 2022-09-29T02:43:05Z
**Labels:** enhancement, config

---

## Original Description

### Current Terraform Version
```
Terraform v0.12.0-alpha4 (2c36829d3265661d8edbd5014de8090ea7e2a076)
```

### Proposal
I like the `object` variable type and it would be nice to be able to define optional arguments which can carry `null` value too, to use:
```hcl
variable "network_rules" {
  default = null
  type = object({
    bypass = optional(list(string))
    ip_rules = optional(list(string))
    virtual_network_subnet_ids = optional(list(string))
  })
}

resource "azurerm_storage_account" "sa" {
  name = random_string.name.result
  location = var.location
  resource_group_name = var.resource_group_name
  account_replication_type = var.account_replication_type
  account_tier = var.account_tier

  dynamic "network_rules" {
    for_each = var.network_rules == null ? [] : list(var.network_rules)

    content {
      bypass = network_rules.value.bypass
      ip_rules = network_rules.value.ip_rules
      virtual_network_subnet_ids = network_rules.value.virtual_network_subnet_ids
    }
  }
```
instead of:
```hcl
variable "network_rules" {
  default = null
  type = map(string)
}

resource "azurerm_storage_account" "sa" {
  name = random_string.name.result
  location = var.location
  resource_group_name = var.resource_group_name
  account_replication_type = var.account_replication_type
  account_tier = var.account_tier

  dynamic "network_rules" {
    for_each = var.network_rules == null ? [] : list(var.network_rules)

    content {
      bypass = lookup(network_rules, "bypass", null) == null ? null : split(",", lookup(network_rules, "bypass"))
      ip_rules = lookup(network_rules, "ip_rules", null) == null ? null : split(",", lookup(network_rules, "ip_rules"))
      virtual_network_subnet_ids = lookup(network_rules, "virtual_network_subnet_ids", null) == null ? null : split(",", lookup(network_rules, "virtual_network_subnet_ids"))
    }
  }
}
```

---

*Resurrected by Resurrection Bot 🧬*
