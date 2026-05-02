
# Configure the DigitalOcean Provider
provider "digitalocean" {
  token = var.digital_ocean_token
}

# Create a module for the droplet
module "droplet" {
  source = "github.com/antarctica/terraform-module-digital-ocean-droplet?ref=v1.0.0"
  hostname = var.hostname
  ssh_fingerprint = var.ssh_fingerprint
}

# Create a module for the DNS records
module "dns_records" {
  source = "github.com/antarctica/terraform-module-digital-ocean-records?ref=v0.1.1"
  hostname = var.hostname
  machine_interface_ipv4_public = module.droplet.ip_v4_address_public
  machine_interface_ipv4_private = module.droplet.ip_v4_address_private
}

# Create a null resource for provisioning
resource "null_resource" "provisioning" {
  depends_on = [module.dns_records]

  # Run an Ansible playbook to provision the droplet
  provisioner "local-exec" {
    command = "ansible-playbook -i provisioning/development provisioning/bootstrap-digitalocean.yml"
  }
}

# Output the IP address of the droplet
output "ip_address" {
  value = module.droplet.ip_v4_address_public
}

# Output the DNS records
output "dns_records" {
  value = module.dns_records.dns_records
}

# Define the variables
variable "digital_ocean_token" {
  type = string
}

variable "hostname" {
  type = string
}

variable "ssh_fingerprint" {
  type = string
}

# Define the locals
locals {
  droplet_name = "${var.hostname}-droplet"
  dns_records_name = "${var.hostname}-dns-records"
}

# Create a resource group for the droplet and DNS records
resource "digitalocean_droplet" "droplet" {
  name   = local.droplet_name
  size   = "s-1vcpu-1gb"
  image  = "ubuntu-20-04-x64"
  region = "nyc1"
}

resource "digitalocean_record" "dns_records" {
  domain = var.hostname
  type   = "A"
  name   = "@"
  value  = digitalocean_droplet.droplet.ipv4_address
}

# Create a null resource for provisioning the droplet
resource "null_resource" "provisioning_droplet" {
  depends_on = [digitalocean_droplet.droplet]

  # Run an Ansible playbook to provision the droplet
  provisioner "local-exec" {
    command = "ansible-playbook -i provisioning/development provisioning/bootstrap-digitalocean.yml"
  }
}

# Output the IP address of the droplet
output "ip_address_droplet" {
  value = digitalocean_droplet.droplet.ipv4_address
}

# Output the DNS records
output "dns_records_droplet" {
  value = digitalocean_record.dns_records
}
