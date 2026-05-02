# aws: Allow rolling updates for ASGs

**Repository:** [hashicorp/terraform](https://github.com/hashicorp/terraform)
**Issue:** [hashicorp/terraform#1552](https://github.com/hashicorp/terraform/issues/1552)
**Reactions:** 70 👍
**Created:** 2015-04-16T09:24:18Z
**Last Activity:** 2017-03-30T06:39:41Z
**Labels:** enhancement, provider/aws

---

## Original Description

Once #1109 is fixed, I'd like to be able to use Terraform to actually roll out the updated launch configuration and do it carefully.

Whoever decides to not roll out the update and change the LC association only should still be allowed to do so.

Here's an example from CloudFormation:
http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-attribute-updatepolicy.html

How about something like this?

``` ruby
resource "aws_autoscaling_group" "test" {
  rolling_update_policy {
    max_batch_size = 1
    min_instances_in_service = 2
    pause_time = "PT0S"
    suspend_processes = ["launch", "terminate"]
    wait_on_resource_signals = true
  }
}
```

then if there's such policy defined, TF can use autoscaling API and shut down each EC2 instance separately and let ASG spin up a new one with an updated LC.


---

*Resurrected by Resurrection Bot 🧬*
