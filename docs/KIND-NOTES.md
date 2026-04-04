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

## Ingress and /etc/hosts

With `cluster/kind-config.yaml` mapping host ports **80** and **443**, and ingress-nginx using `hostPort`, use:

```text
127.0.0.1 whoami.aire-prep.local fake-llm.aire-prep.local
```

## Jaeger UI

Jaeger runs inside the cluster. Example port-forward:

```bash
kubectl port-forward svc/jaeger 16686:16686 -n aire-prep
```

Open http://localhost:16686 and search for service `fake-llm`.

## Image loads

After changing `apps/fake-llm`, rebuild and reload:

```bash
make load-fake-llm
kubectl rollout restart deployment/fake-llm -n aire-prep
```
