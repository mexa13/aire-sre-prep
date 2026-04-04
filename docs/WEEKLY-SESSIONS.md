# Four-week prep schedule (before course start)

**Ordered technical steps (commands + phases):** [START-HERE.md](START-HERE.md). This file is a **weekly narrative** only — not a second source of truth for sequence.

Assume **3–4 sessions per week**, **1.5–2.5 hours** each (or two intensive weekend blocks).

## Week 1 — Kubernetes platform

| Session | Topics | Deliverable |
|---------|--------|-------------|
| A | kind vs k3d vs kubeadm (pick one for speed); CNI, DNS, StorageClass | Running cluster, `kubectl get nodes` |
| B | Ingress + TLS path; cert-manager install | `/etc/hosts` + HTTP to whoami |
| C | Helm: `helm template` / `helm lint` on platform charts | Notes on values you changed |
| Homework | Sketch control plane + request path to ingress | Paper or Excalidraw |

**Lab:** `make cluster-up`, `install-ingress`, `install-cert-manager`, `apply-apps` (whoami only if you defer fake-llm).

## Week 2 — GitOps and controllers

| Session | Topics | Deliverable |
|---------|--------|-------------|
| A | Argo CD (or Flux): bootstrap, sync, drift | App healthy in UI |
| B | Operator mental model: CRD → reconcile (e.g. prometheus-operator via stack) | Short note “what the operator owns” |
| C | GitLess Ops: where AI changes the PR flow vs audit needs | [GITLESS-OPS-NOTES.md](GITLESS-OPS-NOTES.md) |
| Homework | Branch protection + CODEOWNERS on your fork | GitHub settings screenshot optional |

**Lab:** Follow [ARGOCD.md](ARGOCD.md); rollback one revision on purpose.

## Week 3 — Observability

| Session | Topics | Deliverable |
|---------|--------|-------------|
| A | OTel Collector: receivers / processors / exporters | Trace from fake-llm → collector → Jaeger |
| B | Prometheus/Grafana: RPS, p95, error rate panels | 3 panels saved |
| C | Phoenix / OpenInference orientation | UI up or note blockers — see [PHOENIX-OPENINFERENCE.md](PHOENIX-OPENINFERENCE.md) |
| Homework | [RUNBOOK-TRACES.md](RUNBOOK-TRACES.md) filled in | 10–15 lines |

**Lab:** `make install-otel-jaeger`, `make apply-apps`, port-forward Jaeger, generate load on `/v1/chat/completions`.

## Week 4 — MCP, gateways, AI SLO framing

| Session | Topics | Deliverable |
|---------|--------|-------------|
| A | MCP stdio server + client wiring | [MCP.md](MCP.md) checklist done |
| B | AgentGateway / Kagent / `llm-d` smoke (install + one README scenario) | Notes in [COURSE-TOOLS-SMOKE.md](COURSE-TOOLS-SMOKE.md) |
| C | TTFT / TPOT style measurements | Numbers in [SLO-LAB.md](SLO-LAB.md) |
| Homework | [MENTOR-QUESTIONS.md](MENTOR-QUESTIONS.md) | 5–7 questions for day one |

**Lab:** `curl` / `hey` against fake-llm; optional streaming latency experiment.
