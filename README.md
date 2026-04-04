# AI Reliability Engineering — local prep lab

Self-contained material for preparing for the **AI Reliability Engineering 2.0** course: a local Kubernetes lab, GitOps entry point, observability stack, stub workloads, and a minimal MCP server.

## Prerequisites

- Docker (Desktop, Colima, or Linux Docker)
- [kind](https://kind.sigs.k8s.io/) **or** [k3d](https://k3d.io/)
- `kubectl` **>= 1.28**
- `helm` **>= 3.14**
- Python **3.11+** (for local MCP and optional local runs)
- Git + GitHub account (clone/push this repo as your own `k8s-manifests-prep` if you like)

Optional: `k9s`, `hey` or `k6` for load tests (TTFT / latency experiments).

## Quick start

### 1. Create the cluster

```bash
# kind (recommended; maps host 80/443 to ingress)
make cluster-up

# kubeconfig is switched automatically for kind cluster name: aire-prep
kubectl get nodes
```

To tear down:

```bash
make cluster-down
```

 **`cluster-down` deletes the whole cluster** (all namespaces, Helm releases, and images loaded into kind). **`cluster-up` gives you an empty cluster** — you must reinstall everything. Your local Docker image `fake-llm:prep` may still exist on disk, but you need `kind load` again (included in `make apply-apps`).

**Shortcut after recreate:**

```bash
make cluster-up
make bootstrap-lab
# optional: make install-argocd && make apply-argocd-apps
```

### 2. Install platform components

Run installs in order (idempotent Helm upgrades). Resolve Metrics Server on kind if needed — [docs/KIND-NOTES.md](docs/KIND-NOTES.md). Pin chart versions in [docs/VERSION-PINS.md](docs/VERSION-PINS.md).

```bash
make install-platform
```

Or step by step:

```bash
make install-metrics-server
make install-ingress
make install-cert-manager
make install-prometheus
make install-otel-jaeger
```

**OTel/Jaeger** should exist before workloads that export traces (see step 3).

### 3. Build stub image and apply sample apps

```bash
make apply-apps
# Add to /etc/hosts (macOS/Linux):
# 127.0.0.1 whoami.aire-prep.local fake-llm.aire-prep.local
curl -s http://whoami.aire-prep.local
curl -s http://fake-llm.aire-prep.local/health
```

### 4. GitOps (Argo CD)

```bash
make install-argocd
```

Then follow [docs/ARGOCD.md](docs/ARGOCD.md) for the admin password, UI port-forward, and `make apply-argocd-apps` after you set `repoURL` in `gitops/argocd/applications/*.yaml`.

**After Argo syncs the apps**, continue in order: [docs/AFTER-ARGOCD-SYNC.md](docs/AFTER-ARGOCD-SYNC.md).

### 5. Local MCP server (no cluster required)

```bash
cd mcp-server
python -m venv .venv && source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

Wire the server into your MCP client per [docs/MCP.md](docs/MCP.md).

## Repository layout

| Path | Purpose |
|------|---------|
| `cluster/kind-config.yaml` | kind cluster with ingress-ready node and port mappings |
| `Makefile` | Cluster lifecycle and Helm installs |
| `manifests/` | Namespace, apps (whoami, fake-llm), observability, networking samples |
| `apps/fake-llm/` | Stub “LLM-like” HTTP API + Dockerfile (OTel-ready env vars) |
| `gitops/argocd/` | Argo CD application examples |
| `mcp-server/` | Minimal MCP tools server for local practice |
| `docs/` | Weekly session outline, runbook, SLO lab, security notes, course tool smoke tests |
| `grafana/dashboards/` | Grafana JSON dashboards (ingress + workload health); see [grafana/README.md](grafana/README.md) |

## Observability

- **Metrics**: Prometheus / Grafana via `kube-prometheus-stack` (`make install-prometheus`). Which series exist and why: [docs/PROMETHEUS-METRICS-LAB.md](docs/PROMETHEUS-METRICS-LAB.md).
- **Traces**: OpenTelemetry Collector + Jaeger (see `manifests/observability/`).
- **LLM eval UI**: optional Phoenix / OpenInference — [docs/PHOENIX-OPENINFERENCE.md](docs/PHOENIX-OPENINFERENCE.md).

Fake-llm sends OTLP to the collector when `OTEL_EXPORTER_OTLP_ENDPOINT` is set (see Deployment manifest).

## AI / agent gateways (prep smoke tests only)

Course tools evolve quickly. Use official READMEs and pin versions; see [docs/COURSE-TOOLS-SMOKE.md](docs/COURSE-TOOLS-SMOKE.md) for Agent Gateway, Kagent, `llm-d`, and related links.

## Weekly study plan

Structured sessions are in [docs/WEEKLY-SESSIONS.md](docs/WEEKLY-SESSIONS.md) (aligned with the four prep weeks before the course).

## License

MIT — prep materials only; not affiliated with the course provider.
