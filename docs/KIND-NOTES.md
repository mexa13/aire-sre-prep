# kind-specific notes

## metrics-server kind / TLS errors

Symptoms: `x509: cannot validate certificate for … because it doesn't contain any IP SANs` and `no metrics to serve`. Upstream **v0.8.x** also sets `--kubelet-use-node-status-port`; on kind you still need **`--kubelet-insecure-tls`** so metrics-server trusts the kubelet serving cert (no IP SAN for the node IP).

Without that flag, the Deployment may never reach **Available**, and waiting for rollout **before** patching can block or look “stuck”. `make install-metrics-server` applies the patch **immediately** after `kubectl apply`, then runs a single `kubectl rollout status`.

If you installed manifests by hand:

```bash
kubectl patch deployment metrics-server -n kube-system --type='json' \
  -p='[{"op": "add", "path": "/spec/template/spec/containers/0/args/-", "value": "--kubelet-insecure-tls"}]'
kubectl rollout status deployment/metrics-server -n kube-system --timeout=180s
kubectl top nodes
```

Still failing? Check that the flag is present: `kubectl get deploy metrics-server -n kube-system -o jsonpath='{.spec.template.spec.containers[0].args}'`. As a last resort for kind, some clusters work after removing the `--kubelet-use-node-status-port` argument via `kubectl edit deployment metrics-server -n kube-system`.

If you only need the rest of the lab, metrics issues **do not** block ingress, workloads, or tracing; they only affect `kubectl top` and HPAs that use the metrics API.

## ingress-nginx: `no free ports for the requested pod ports`

With **hostPort** `80`/`443` on a **single-node** kind cluster, a default **RollingUpdate** can schedule a **new** controller pod while the **old** one still runs. Both need the same host ports → scheduling fails.

The lab [helm/ingress-nginx-values.yaml](../helm/ingress-nginx-values.yaml) sets `controller.updateStrategy.type: Recreate` and `replicaCount: 1` to avoid that. Re-run `make install-ingress` after pulling.

If you still see the error, check no second replica or autoscaling: `kubectl get deploy -n ingress-nginx -o wide`.

## Lab hostnames (ingress)

kind maps **80**/**443** on the host to ingress-nginx ([cluster/kind-config.yaml](../cluster/kind-config.yaml)). Add to **`/etc/hosts`**:

```text
127.0.0.1 whoami.aire-prep.local fake-llm.aire-prep.local grafana.aire-prep.local prometheus.aire-prep.local alertmanager.aire-prep.local jaeger.aire-prep.local argocd.aire-prep.local
```

Skip `argocd.aire-prep.local` until you run `make install-argocd`.

**Wildcards:** `/etc/hosts` does **not** support `*.aire-prep.local` (or any pattern). Each hostname must appear literally; you can put several names on one line after the IP.

| URL | What |
|-----|------|
| http://whoami.aire-prep.local | whoami echo |
| http://fake-llm.aire-prep.local | Stub LLM HTTP API |
| http://grafana.aire-prep.local | Grafana (stack Helm release `kube-prometheus`) |
| http://prometheus.aire-prep.local | Prometheus UI |
| http://alertmanager.aire-prep.local | Alertmanager UI |
| http://jaeger.aire-prep.local | Jaeger UI |
| http://argocd.aire-prep.local | Argo CD UI (HTTP; `configs.params.server.insecure` in [helm/argocd-values.yaml](../helm/argocd-values.yaml)) |

**Existing cluster:** after `git pull`, re-apply observability and upgrade Helm releases so Ingress objects exist:

```bash
kubectl apply -k manifests/observability/
make install-prometheus
make install-argocd   # if you use Argo
```

## Jaeger UI

Prefer **`http://jaeger.aire-prep.local`** (Ingress in [manifests/observability/jaeger-ingress.yaml](../manifests/observability/jaeger-ingress.yaml)).

Port-forward fallback:

```bash
kubectl port-forward svc/jaeger 16686:16686 -n aire-prep
```

Open `http://localhost:16686` and search for service `fake-llm`.

## Image loads

After changing `apps/fake-llm`, rebuild and reload:

```bash
make load-fake-llm
kubectl rollout restart deployment/fake-llm -n aire-prep
```
