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

Add your resolved versions below when locking the lab for May 2026:

```text
ingress-nginx:
cert-manager:
kube-prometheus-stack:
```
