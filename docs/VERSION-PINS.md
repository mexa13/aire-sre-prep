# Version pins (update deliberately)

Record Helm chart versions after `helm list` / `helm search repo` so the course environment stays reproducible.

| Component | Example pin approach |
|-----------|---------------------|
| kind node | Kubernetes version implied by your kind release |
| ingress-nginx | `helm search repo ingress-nginx/ingress-nginx --versions` |
| cert-manager | `helm search repo jetstack/cert-manager --versions` |
| kube-prometheus-stack | `helm search repo prometheus-community/kube-prometheus-stack --versions` |
| argo-cd | `helm search repo argo/argo-cd --versions` (after `helm repo add argo ...`) |
| otel-collector | Image tag in `manifests/observability/otel-collector.yaml` |
| Jaeger | Image tag in `manifests/observability/jaeger.yaml` |
| fake-llm deps | `apps/fake-llm/requirements.txt` |
| **kagent** | Git tag / chart version from [github.com/kagent-dev/kagent](https://github.com/kagent-dev/kagent) after smoke test |
| **agentgateway** | Image tag / chart from [github.com/agentgateway/agentgateway](https://github.com/agentgateway/agentgateway) releases or install manifest |
| **llm-d** | Release / chart from [github.com/llm-d/llm-d](https://github.com/llm-d/llm-d) after smoke test |
| **kmcp** | `kmcp version` or release from [github.com/kagent-dev/kmcp](https://github.com/kagent-dev/kmcp) |
| **google-adk** | `pip show google-adk` after Phase K ADK smoke |
| **A2A samples** | Git commit or sample path you ran from [github.com/a2aproject/A2A](https://github.com/a2aproject/A2A) (if you do A2A smoke) |

## Resolved pins (fill from your cluster)

```text
ingress-nginx:
cert-manager:
kube-prometheus-stack:
kagent: (after COURSE-TOOLS-SMOKE)
agentgateway: chart agentgateway=v1.0.1, chart agentgateway-crds=v1.0.1, controller image=cr.agentgateway.dev/controller:v1.0.1
llm-d:
kmcp:
google-adk:
a2a-sample:
```
