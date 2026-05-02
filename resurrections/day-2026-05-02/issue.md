# Depends_on for module

**Repository:** [hashicorp/terraform](https://github.com/hashicorp/terraform)
**Issue:** [hashicorp/terraform#1178](https://github.com/hashicorp/terraform/issues/1178)
**Reactions:** 136 👍
**Created:** 2015-03-11T09:39:55Z
**Last Activity:** 2019-07-24T01:57:09Z
**Labels:** enhancement, core, thinking

---

## Original Description

#### Possible workarounds

For module to module dependencies, [this workaround](https://github.com/hashicorp/terraform/issues/1178#issuecomment-105613781) by @phinze may help.
#### Original problem

This issue was promoted by [this](https://groups.google.com/forum/#!topic/terraform-tool/aQd-MJAcE6A) question on Google Groups.

Terraform version: `Terraform v0.3.7`

I have two terraform modules for creating a digital ocean VM and DNS records that are kept purposely modular so they can be reused by others in my organisation.

I want to add a series of provisioners using local_exec after a VM has been created and DNS records made.
#### Attempted solution

I tried adding a provisioner directly to my terraform file (i.e. not in a resource) which gave an error.

I then tried using the `null_resource` which worked but was executed at the wrong time as it didn't know to wait for the other modules to execute first.

I then tried adding a `depends_on` attribute to the null resource using a reference to a module but this doesn't seem to be supported using this syntax:

```
depends_on = ["module.module_name"]
```
#### Expected result

Either a way for a resource to depend on a module as a dependency or a way to "inject" (for lack of a better word) some provisioners for a resource into a module without having to make a custom version of that module (I realise that might be a separate issue but it would solve my original problem).
#### Terraform config used

```
# Terraform definition file - this file is used to describe the required infrastructure for this project.

# Digital Ocean provider configuration

provider "digitalocean" {
    token = "${var.digital_ocean_token}"
}


# Resources

# 'whoosh-dev-web1' resource

# VM

module "whoosh-dev-web1-droplet" {
    source = "github.com/antarctica/terraform-module-digital-ocean-droplet?ref=v1.0.0"
    hostname = "whoosh-dev-web1"
    ssh_fingerprint = "${var.ssh_fingerprint}"
}

# DNS records (public, private and default [which is an APEX record and points to public])

module "whoosh-dev-web1-records" {
    source = "github.com/antarctica/terraform-module-digital-ocean-records?ref=v0.1.1"
    hostname = "whoosh-dev-web1"
    machine_interface_ipv4_public = "${module.whoosh-dev-web1-droplet.ip_v4_address_public}"
    machine_interface_ipv4_private = "${module.whoosh-dev-web1-droplet.ip_v4_address_private}"
}


# Provisioning (using a fake resource as provisioners can't be first class objects)

# Note: The "null_resource" is an undocumented feature and should not be relied upon.
# See https://github.com/hashicorp/terraform/issues/580 for more information.

resource "null_resource" "provisioning" {

    depends_on = ["module.whoosh-dev-web1-records"]

    # This replicates the provisioning steps performed by Vagrant
    provisioner "local-exec" {
        command = "ansible-playbook -i provisioning/development provisioning/bootstrap-digitalocean.yml"
    }
}
```


---

*Resurrected by Resurrection Bot 🧬*
