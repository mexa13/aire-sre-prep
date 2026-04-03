# kind-specific notes

## metrics-server kind / TLS errors

Symptoms: `x509: cannot validate certificate for … because it doesn't contain any IP SANs` and `no metrics to serve`. This is **normal on kind**; it does **not** block ingress, workloads, or tracing for this lab. It only breaks `kubectl top` and features that need the metrics API (e.g. some HPAs).

`make install-metrics-server` already applies `--kubelet-insecure-tls` after install. If you installed manifests by hand, run:

```bash
kubectl patch deployment metrics-server -n kube-system --type='json' \
  -p='[{"op": "add", "path": "/spec/template/spec/containers/0/args/-", "value": "--kubelet-insecure-tls"}]'
kubectl rollout status deployment/metrics-server -n kube-system --timeout=120s
```

Wait until `kubectl top nodes` works.

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
