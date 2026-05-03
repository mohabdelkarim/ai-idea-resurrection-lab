# Improving perception of changes when showing diff

**Repository:** [hashicorp/terraform](https://github.com/hashicorp/terraform)
**Issue:** [hashicorp/terraform#15180](https://github.com/hashicorp/terraform/issues/15180)
**Reactions:** 36 👍
**Created:** 2017-06-08T02:47:53Z
**Last Activity:** 2019-02-20T02:18:18Z
**Labels:** enhancement, cli

---

## Original Description

When I make a change to a large list of values (for example), the plan that Terraform shows is not as helpful as it could be. Here is what I see:

<img width="655" alt="screenshot of terminal 8-06-17 3-16-32 pm" src="https://user-images.githubusercontent.com/811954/26910840-7ba93d92-4c5d-11e7-998f-f3533d169ef0.png">

There are three important pieces of information here, but only one is clear:

1. The resource `google_project_services.project` is changing (this is clear from colouring)
2. The number of services in the list is changing from 21 -> 20
3. The service that is being removed is "container.googleapis.com"

There is so much going on in the output that it is hard to easily see the relevant information. I have thought of some possible ways the output could be improved:

* Highlighting lines that are changing with their related change colour (green, yellow, red for add, change, destroy respectively)
* Aligning all of the `=>` so it is easier to scan for changes
* De-emphasising the hash (133405307) with a lighter colour as it's specific value is usually not very important (I think?)
* Sorting attributes that are changing to the top
* Removing unchanged attributes from the diff

I haven't really considered how default and computed values would be handled here, but it seems highly relevant and important.

Some mockups:

**Highlighting changed lines and deemphasising hash**

<img width="652" alt="screenshot of terminal 8-06-17 3-17-41 pm" src="https://user-images.githubusercontent.com/811954/26910871-ae8f5804-4c5d-11e7-9302-1c2f3d3aa658.png">


**Align =>**

```
~ google_project_services.project
    services.#:          "21" => "20"
    services.133405307:  "storage-component.googleapis.com"    => "storage-component.googleapis.com"
    services.1560437671: "iam.googleapis.com"                  => "iam.googleapis.com"
    services.1712537408: "containerregistry.googleapis.com"    => "containerregistry.googleapis.com"
    services.2117420113: "pubsub.googleapis.com"               => "pubsub.googleapis.com"
    services.238136042:  "cloudapis.googleapis.com"            => "cloudapis.googleapis.com"
    services.2471815660: "servicemanagement.googleapis.com"    => "servicemanagement.googleapis.com"
    services.2631575801: "sqladmin.googleapis.com"             => "sqladmin.googleapis.com"
    services.2928564140: "dns.googleapis.com"                  => "dns.googleapis.com"
    services.2966512281: "deploymentmanager.googleapis.com"    => "deploymentmanager.googleapis.com"
    services.3010261123: "replicapool.googleapis.com"          => "replicapool.googleapis.com"
    services.3075019877: "replicapoolupdater.googleapis.com"   => "replicapoolupdater.googleapis.com"
    services.3077910291: "resourceviews.googleapis.com"        => "resourceviews.googleapis.com"
    services.323125032:  "cloudtrace.googleapis.com"           => "cloudtrace.googleapis.com"
    services.3237295688: "monitoring.googleapis.com"

---

*Resurrected by Resurrection Bot 🧬*
