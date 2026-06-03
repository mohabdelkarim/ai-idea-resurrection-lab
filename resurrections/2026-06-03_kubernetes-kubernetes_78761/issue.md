# HPA doesn't scale down to minReplicas even though metric is under target

**Repository:** [kubernetes/kubernetes](https://github.com/kubernetes/kubernetes)
**Issue:** [kubernetes/kubernetes#78761](https://github.com/kubernetes/kubernetes/issues/78761)
**Reactions:** 89 👍
**Created:** 2019-06-06T11:59:43Z
**Last Activity:** 2023-09-25T17:33:00Z
**Labels:** kind/bug, sig/autoscaling

---

## Original Description

**What happened**:

HPA scales to `Spec.MaxReplicas` even though metric is always under target.

Here's the HPA in YAML:

```yaml
apiVersion: autoscaling/v1
kind: HorizontalPodAutoscaler
metadata:
  annotations:
    autoscaling.alpha.kubernetes.io/conditions: '[{"type":"AbleToScale","status":"True","lastTransitionTime":"2019-06-06T10:46:13Z","reason":"ReadyForNewScale","message":"recommended
      size matches current size"},{"type":"ScalingActive","status":"True","lastTransitionTime":"2019-06-06T10:46:13Z","reason":"ValidMetricFound","message":"the
      HPA was able to successfully calculate a replica count from cpu resource utilization
      (percentage of request)"},{"type":"ScalingLimited","status":"True","lastTransitionTime":"2019-06-06T10:46:13Z","reason":"TooManyReplicas","message":"the
      desired replica count is more than the maximum replica count"}]'
    autoscaling.alpha.kubernetes.io/current-metrics: '[{"type":"Resource","resource":{"name":"cpu","currentAverageUtilization":0,"currentAverageValue":"9m"}}]'
  creationTimestamp: "2019-06-06T10:45:58Z"
  name: my-app-1
  namespace: default
  resourceVersion: "55041251"
  selfLink: /apis/autoscaling/v1/namespaces/default/horizontalpodautoscalers/my-app-1
  uid: 44fedc1a-8848-11e9-8465-025acf90d81e
spec:
  maxReplicas: 4
  minReplicas: 2
  scaleTargetRef:
    apiVersion: extensions/v1beta1
    kind: Deployment
    name: my-app-1
  targetCPUUtilizationPercentage: 40
status:
  currentCPUUtilizationPercentage: 0
  currentReplicas: 4
  desiredReplicas: 4
```

And here's a description output:

```
$ kubectl describe hpa my-app-1
  Name:                                                  my-app-1
  Namespace:                                             default
  Labels:                                                <none>
  Annotations:                                           <none>
  CreationTimestamp:                                     Thu, 06 Jun 2019 12:45:58 +0200
  Reference:                                             Deployment/my-app-1
  Metrics:                                               ( current / target )
    resource cpu on pods  (as a percentage of request):  0% (9m) / 40%
  Min replicas:                                          2
  Max replicas:                                          4
  Deployment pods:                                       4 current / 4 desired
  Conditions:
    Type            Status  Reason            Message
    ----            ------  ------            -------
    AbleToScale     True    ReadyForNewScale  recommended size matches current size
    ScalingActive   True    ValidMetricFound  the HPA was able to successfully calculate a replica count from cpu resource utilization (percentage of request)
    ScalingLimited  True    TooManyReplicas   the desired replica count is more than the maximum replica count
  Events:           <none>
```

**What you expected to happen**:

HPA only scal

---

*Resurrected by Resurrection Bot 🧬*
