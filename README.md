# AI Reliability Engineering — local prep lab

Self-contained material for preparing for the **AI Reliability Engineering 2.0** course: a local Kubernetes lab, GitOps entry point, observability stack, stub workloads, and a minimal MCP server.

## Where to start (read this first)

**[docs/START-HERE.md](docs/START-HERE.md)** — the **only** ordered checklist: phases A→L, what each step does, `kubectl` / `curl` / `make` commands, and links to deeper docs. Everything else in `docs/` is an appendix.

**Heads-up:** sample apps (whoami, fake-llm) are created by **`kubectl apply`** inside `make bootstrap-lab`. **Argo CD is optional** and comes later if you want GitOps — see the “Read this before Phase C” box in START-HERE.

---

## Prerequisites

- Docker (Desktop, Colima, or Linux Docker)
- [kind](https://kind.sigs.k8s.io/) **or** [k3d](https://k3d.io/)
- `kubectl` **>= 1.28**
- `helm` **>= 3.14**
- Python **3.11+** (for MCP in Phase J of START-HERE)
- Git + GitHub account (for Argo GitOps)

Optional: `k9s`, `hey` or `k6` for load tests.

**Fast recreate after `make cluster-down`:**

```bash
make cluster-up
make bootstrap-lab
# optional GitOps: make install-argocd && make apply-argocd-apps
```

**Local URLs:** Grafana, Prometheus, Alertmanager, Jaeger, sample apps, and (after Argo install) Argo CD are exposed via **ingress** on `*.aire-prep.local`. Add lines to `/etc/hosts` as in [docs/KIND-NOTES.md](docs/KIND-NOTES.md#lab-hostnames-ingress).

---

## Repository layout

| Path | Purpose |
|------|---------|
| [docs/START-HERE.md](docs/START-HERE.md) | **Main prep order** (start here) |
| `cluster/kind-config.yaml` | kind cluster with ingress-ready node and port mappings |
| `Makefile` | Cluster lifecycle and Helm installs |
| `manifests/` | Namespace, apps (whoami, fake-llm), observability, optional `cert-lab/` |
| `apps/fake-llm/` | Stub “LLM-like” HTTP API + Dockerfile |
| `gitops/argocd/` | Argo CD application examples |
| `mcp-server/` | Minimal MCP tools — [START-HERE Phase J](docs/START-HERE.md), wiring + LM Studio: [MCP.md](docs/MCP.md) |
| `docs/` | Appendices: metrics, TLS, runbook templates, course smoke, etc. |
| `grafana/dashboards/` | Grafana JSON imports — [grafana/README.md](grafana/README.md) |

---

## Pointers (details live in START-HERE + linked docs)

- **Metrics / Grafana:** [docs/PROMETHEUS-METRICS-LAB.md](docs/PROMETHEUS-METRICS-LAB.md)
- **Traces:** Jaeger in START-HERE Phase F; runbook template [docs/RUNBOOK-TRACES.md](docs/RUNBOOK-TRACES.md)
- **Optional TLS:** [docs/TLS-CERT-MANAGER-LAB.md](docs/TLS-CERT-MANAGER-LAB.md)
- **Phoenix:** [docs/PHOENIX-OPENINFERENCE.md](docs/PHOENIX-OPENINFERENCE.md)
- **Course tool smoke:** [docs/COURSE-TOOLS-SMOKE.md](docs/COURSE-TOOLS-SMOKE.md)
- **4-week narrative (optional):** [docs/WEEKLY-SESSIONS.md](docs/WEEKLY-SESSIONS.md)

**Old link:** [docs/AFTER-ARGOCD-SYNC.md](docs/AFTER-ARGOCD-SYNC.md) → redirects to START-HERE Phase E+.

## License

MIT — prep materials only; not affiliated with the course provider.
