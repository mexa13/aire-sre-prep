# Prometheus / Grafana in this lab — what exists and why

## Not a namespace scrape problem

`kube-prometheus-stack` scrapes **targets** defined by:

- Kubernetes API (kubernetes-apiservers, kubelet/cAdvisor, etc.)
- **kube-state-metrics** (objects like Pods, Deployments — includes every namespace)
- **node-exporter**
- Any **ServiceMonitor** / **PodMonitor** in the cluster

Prometheus does **not** “skip” namespaces for container metrics. If you see:

```promql
container_cpu_usage_seconds_total{namespace="aire-prep"}
```

then data for `aire-prep` is already being collected.

## Why `http_requests_total` / `http_request_duration_seconds_bucket` are empty

Those names usually come from:

- An application that exposes a **`/metrics`** endpoint using the Prometheus client, or
- A middleware that records HTTP metrics with those exact names.

**whoami** and **fake-llm** in this repo are **not** instrumented for Prometheus (they use OTel for traces, not Prometheus histograms for HTTP). So those series will **not** appear unless you add code + a scrape config.

## The `up` metric

`up` is **per scrape target** (labels like `job`, `instance`, `pod`). Many jobs **do not** have a `namespace` label, so a query like:

```promql
up{namespace="aire-prep"}
```

often returns **nothing** even when everything works. Prefer:

```promql
up
```

or filter by `job`:

```promql
up{job=~".*ingress.*"}
```

## HTTP-style metrics: use ingress-nginx

After enabling metrics in [helm/ingress-nginx-values.yaml](../helm/ingress-nginx-values.yaml), upgrade the release and wait ~1–2 minutes for the ServiceMonitor to be picked up:

```bash
make install-ingress
```

Useful metrics (names may vary slightly by chart version; check **Metrics explorer** or **Explore**):

```promql
# Request rate (adjust ingress label to your ingress name/host if needed)
sum(rate(nginx_ingress_controller_requests[5m])) by (ingress)

# Request duration histogram
histogram_quantile(0.95, sum(rate(nginx_ingress_controller_request_duration_seconds_bucket[5m])) by (le, ingress))
```

If series are still missing: `kubectl get servicemonitor -A` and confirm one exists for ingress-nginx in namespace `ingress-nginx`.

## Generating 502 / non-2xx when apps are managed by Argo CD

If the Application has `syncPolicy.automated.selfHeal: true` (see [gitops/argocd/applications/app-aire-prep-apps.yaml](../gitops/argocd/applications/app-aire-prep-apps.yaml)), **manual `kubectl scale`** is reverted: Git says `replicas: 1`, so Argo restores the Deployment and pods come back — `curl` keeps returning **200**.

Pick one approach:

**A — Pause Argo for a few minutes (UI)**  
Open Application **aire-prep-apps** → **App details** → **Pause** (or disable **Auto-Heal** / set sync to manual, depending on UI version). Then:

```bash
kubectl scale deployment/fake-llm -n aire-prep --replicas=0
# generate traffic, then scale back and resume Argo
kubectl scale deployment/fake-llm -n aire-prep --replicas=1
```

**B — CLI**  
Use `argocd app set --help` for your version to turn off automated sync or self-heal on `aire-prep-apps`, then scale and test, then restore the previous sync policy.

**C — Git is the source of truth**  
Commit `replicas: 0` in `manifests/apps/fake-llm/deployment.yaml`, push, let Argo sync, run load tests, then revert to `replicas: 1` and push again. No drift, no fight with self-heal.

**D — Break the Service without changing replicas**  
Temporarily point the Service selector to a label that matches no pods (edit Service or patch), generate traffic, then restore. Argo may still revert if the Service is in the same Application — same self-heal rules apply.

For a quick lab, **A** or **C** is usually clearest.

## Grafana variables + `No data` on filtered queries

If unfiltered queries work but this returns nothing:

```promql
sum(rate(nginx_ingress_controller_requests{namespace="$namespace",status!~"2..",ingress=~"$ingress"}[5m])) by (ingress)
```

check the following:

1. **Same Prometheus UID everywhere**  
   Panel datasource and **each templating variable** must use the **same** datasource UID (e.g. `prometheus`). A placeholder like `PROMETHEUS_UID` in variable JSON breaks variable queries → empty `$namespace` / `$ingress` → `namespace=""` matches no series.

2. **Verify labels in Explore** (no variables):

   ```promql
   sum(rate(nginx_ingress_controller_requests[5m])) by (namespace, ingress, status)
   ```

   Confirm the literal values for `namespace` (often `aire-prep`) and `ingress` (e.g. `fake-llm`, `whoami` — **Ingress object name**, not hostname).

3. **“All” for `ingress`**  
   With **Include all**, Grafana usually sets `$ingress` to `.*` for regex matchers — OK for `ingress=~"$ingress"`. If **All** still breaks, try a fixed test: `ingress="fake-llm"` (exact match, no regex).

4. **Multi-select**  
   Grafana joins values with `|`; `ingress=~"$ingress"` should work. If not, switch variable to **single** select for debugging.

5. **Optional: drop `namespace`** if your controller version exposes fewer labels — use only `ingress=~"$ingress"` once labels from step 2 are confirmed.

## Panels that work without ingress metrics

Until ingress metrics appear, you can still build the “three panel” exercise:

**CPU (aire-prep)**

```promql
sum(rate(container_cpu_usage_seconds_total{namespace="aire-prep", container!=""}[5m])) by (pod)
```

**Restarts**

```promql
sum(kube_pod_container_status_restarts_total{namespace="aire-prep"}) by (pod)
```

**“Errors” proxy — pods not ready**

```promql
sum(kube_pod_status_ready{namespace="aire-prep", condition="true"})
```

or compare running vs desired:

```promql
kube_deployment_spec_replicas{namespace="aire-prep"} - kube_deployment_status_replicas_available{namespace="aire-prep"}
```

These are valid for a prep dashboard even though they are not HTTP RED metrics.
