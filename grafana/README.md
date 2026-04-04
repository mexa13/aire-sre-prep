# Grafana dashboards (prep lab)

**When in the prep path:** [docs/START-HERE.md](../docs/START-HERE.md) **Phase G — Grafana dashboards**.

JSON exports for import into Grafana bundled with `kube-prometheus-stack`.

## Import

1. Port-forward Grafana: `kubectl port-forward -n monitoring svc/kube-prometheus-grafana 3000:80` (adjust release name if yours differs).
2. **Dashboards → New → Import → Upload JSON file**.
3. Select the **Prometheus** datasource when prompted (or ensure a datasource exists with **UID `prometheus`** — kube-prometheus-stack often registers it that way; if your UID differs, use **Import → Options → Prometheus** dropdown or edit each panel datasource).

## Files

| File | Description |
|------|-------------|
| [dashboards/aire-prep-ingress-overview.json](dashboards/aire-prep-ingress-overview.json) | Ingress request rate, p95 latency, non-2xx rate (`nginx_ingress_controller_*`). Variables: namespace, ingress. |
| [dashboards/aire-prep-workload-health.json](dashboards/aire-prep-workload-health.json) | Pod restarts, CPU, memory for `aire-prep` workloads matching `fake-llm*` / `whoami*`. |

Ingress metrics require [helm/ingress-nginx-values.yaml](../helm/ingress-nginx-values.yaml) metrics + ServiceMonitor (`make install-ingress`).

See also [docs/PROMETHEUS-METRICS-LAB.md](../docs/PROMETHEUS-METRICS-LAB.md).
