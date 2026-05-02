# offer to create missing bucket and lock_table for s3 backend

**Repository:** [hashicorp/terraform](https://github.com/hashicorp/terraform)
**Issue:** [hashicorp/terraform#12780](https://github.com/hashicorp/terraform/issues/12780)
**Reactions:** 59 👍
**Created:** 2017-03-16T20:34:54Z
**Last Activity:** 2018-12-27T06:32:57Z
**Labels:** enhancement, backend/s3

---

## Original Description

### Terraform Version
Terraform v0.9.0

### Affected Resource(s)
- s3 backend

### Terraform Configuration Files
```hcl
terraform {
  required_version = ">= 0.9"

  backend "s3" {
    region = "us-east-2"
    lock_table = "table-xi0s3p59prd9mubqsinc"
    encrypt = "true"
    bucket = "bucket-xi0s3p59prd9mubqsinc"
    key = "test/terraform.tfstate" 
  }
}

provider "aws" {
  region = "us-east-2"
}

resource "aws_sns_topic" "foo" {
    name = "foo-topic"
}
```

### Feature Request

I'm very excited about the new backend configuration in Terraform 0.9, but it's inconvenient that I have to manually create both an S3 bucket and a DynamoDB table before I can get started.  (If I enjoyed manually creating resources, I wouldn't need Terraform!)

*Terragrunt* (with Terraform <= 0.8.x) handles this extremely conveniently by:
1. Prompting the user to automatically create the S3 bucket if it doesn't exist.
2. If user says yes, creating the bucket **and enabling versioning**.
3. Automatically creating the DynamoDB lock table if it doesn't exist.

I would love to see Terraform 0.9+ do the same (perhaps during `terraform init`?)

Here's how the equivalent configuration behaves using Terragrunt, starting from a blank slate:
```
$ terragrunt apply
[terragrunt] 2017/03/16 14:57:20 Reading Terragrunt config file at /home/dmrz/aws/dmrz-test/bar/terraform.tfvars
[terragrunt] 2017/03/16 14:57:20 Initializing remote state for the s3 backend
[terragrunt]  Remote state S3 bucket bucket-xi0s3p59prd9mubqsinc does not exist or you don't have permissions to access it. Would you like Terragrunt to create it? (y/n) y
[terragrunt] 2017/03/16 14:57:22 Creating S3 bucket bucket-xi0s3p59prd9mubqsinc
[terragrunt] 2017/03/16 14:57:22 S3 bucket bucket-xi0s3p59prd9mubqsinc created.
[terragrunt] 2017/03/16 14:57:22 Enabling versioning on S3 bucket bucket-xi0s3p59prd9mubqsinc
[terragrunt] 2017/03/16 14:57:23 Configuring remote state for the s3 backend
[terragrunt] 2017/03/16 14:57:23 Running command: /usr/local/libexec/terraform-0.8.7 remote config -backend s3 -backend-config=encrypt=true -backend-config=bucket=bucket-xi0s3p59prd9mubqsinc -backend-config=key=test/terraform.tfstate -backend-config=region=us-east-2
Initialized blank state with remote state enabled!
Remote state configured and pulled.
[terragrunt] 2017/03/16 14:57:24 Attempting to acquire lock for state file state in DynamoDB
[terragrunt] 2017/03/16 14:57:25 Lock table table-xi0s3p59prd9mubqsinc does not exist in DynamoDB. Will need to create it just this first time.
[terragrunt] 2017/03/16 14:57:25 Creating table table-xi0s3p59prd9mubqsinc in DynamoDB
[terragrunt] 2017/03/16 14:57:25 Table table-xi0s3p59prd9mubqsinc is not yet in active state. Will check again after 10s.
[terragrunt] 2017/03/16 14:57:35 Success! Table table-xi0s3p59prd9mubqsinc is now in active state.
[terragrunt] 2017/03/16 14:57:35 Attempting to create lock item for state file state in DynamoDB ta

---

*Resurrected by Resurrection Bot 🧬*
