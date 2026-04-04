# Prep lab — do this in order

**One file = order of operations.** Other `docs/*.md` files are only for extra detail when you are stuck.

**Prerequisites:** Docker, [kind](https://kind.sigs.k8s.io/), `kubectl`, `helm`, Git, Python 3.11+ (MCP only). Optional: `hey` / `k6`. See [README](../README.md#prerequisites).

---

## Read this before Phase C (common confusion)

**`curl` to whoami / fake-llm does not need Argo.**

- **`make bootstrap-lab`** ends with **`make apply-apps`**, which runs **`kubectl apply`** on [manifests/apps](../manifests/apps/). That creates pods, Services, and Ingress **directly**. Ingress-nginx sends traffic to them. **Argo CD is not used in that step.**
- **Phase D (Argo)** is **optional**: add it if you want GitOps. If you add it, Argo keeps applying the **same YAML** from Git—it replaces nothing magical for the first `curl`.

**Two valid ways to get to a working `curl`:**

| Way | What you run | When `curl` works |
|-----|----------------|-------------------|
| **A — Makefile (simplest)** | Phase B → **Phase C** (`make bootstrap-lab`) | Right after Phase C, if `/etc/hosts` is set and pods are Running. |
| **B — GitOps only** | Phase B → `install-platform` + `install-otel-jaeger` → **Phase D** (Argo + sync apps) — **no** `bootstrap-lab` | Only **after** Argo has synced `aire-prep-apps` (and you ran `make load-fake-llm` if the image is local). |

Default path below is **Way A**. If you use **Way B**, skip Phase C’s `bootstrap-lab` and do not run `curl` until Phase D is green.

---

## Phase A — Makefile reference (what each target does)

| Target | What it does |
|--------|----------------|
| `make cluster-up` | kind cluster + `aire-prep` namespace |
| `make cluster-down` | Deletes entire cluster |
| `make install-platform` | metrics-server, ingress, cert-manager, Prometheus stack (no sample apps) |
| `make install-otel-jaeger` | OTel + Jaeger in `aire-prep` |
| `make apply-apps` | `docker build` fake-llm, `kind load`, **`kubectl apply -k manifests/apps`** |
| `make bootstrap-lab` | `install-platform` + `apply-apps` (**still no Argo**) |
| `make install-argocd` | Helm: Argo CD |
| `make apply-argocd-apps` | `kubectl apply` Argo `Application` CRs (your Git repo URL in YAML) |

kind edge cases: [KIND-NOTES.md](KIND-NOTES.md).

---

## Phase B — Create the cluster

**Goal:** Empty cluster, context `kind-aire-prep`.

```bash
cd /path/to/aire-sre-prep
make cluster-up
kubectl get nodes
```

---

## Phase C — Platform + sample apps (Way A — no Argo)

**Goal:** whoami + fake-llm + ingress + observability stack. **Deployed by kubectl, not by Argo.**

```bash
make bootstrap-lab
```

`/etc/hosts`:

```text
127.0.0.1 whoami.aire-prep.local fake-llm.aire-prep.local
```

**Prove the path:** pods exist **without** any `argocd` namespace required:

```bash
kubectl get pods,svc,ingress -n aire-prep
curl -sS http://whoami.aire-prep.local | head
curl -sS http://fake-llm.aire-prep.local/health
```

If `curl` fails: `kubectl get pods -n ingress-nginx`, `kubectl describe ingress -n aire-prep`, [KIND-NOTES.md](KIND-NOTES.md).

**More:** [Makefile](../Makefile), [PROMETHEUS-METRICS-LAB.md](PROMETHEUS-METRICS-LAB.md).

---

## Phase D — GitOps with Argo CD (optional)

**Goal:** Same manifests tracked from Git; rollback / drift practice later.

**Skip** if you only care about kubectl-managed lab.

```bash
make install-argocd
kubectl -n argocd get secret argocd-initial-admin-secret -o jsonpath='{.data.password}' | base64 -d; echo
kubectl port-forward svc/argocd-server -n argocd 8080:443
```

1. UI `https://localhost:8080` → `admin` + password above.  
2. Set `repoURL` in `gitops/argocd/applications/*.yaml`.  
3. `make apply-argocd-apps`  
4. `ImagePullBackOff` on fake-llm → `make load-fake-llm` → **Refresh** in Argo.

**Way B only:** if you did **not** run Phase C, your **first** successful `curl` happens **after** apps show Synced/Healthy here.

**More:** [ARGOCD.md](ARGOCD.md).

---

## Phase E — Re-check workloads (if you use Argo)

**Skip** if you did not install Argo.

**Goal:** Cluster matches Git; HTTP still works.

```bash
kubectl get pods,svc,ingress -n aire-prep
curl -sS http://fake-llm.aire-prep.local/health
```

```bash
curl -sS -X POST http://fake-llm.aire-prep.local/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"model":"fake","messages":[{"role":"user","content":"hi"}]}'
```

---

## Phase F — Jaeger traces

**Goal:** See traces after traffic to fake-llm.

```bash
kubectl port-forward svc/jaeger 16686:16686 -n aire-prep
```

Browser: `http://localhost:16686` → service **fake-llm**.

**More:** [RUNBOOK-TRACES.md](RUNBOOK-TRACES.md).

---

## Phase G — Grafana

**Goal:** Metrics UI + optional JSON dashboards.

```bash
kubectl port-forward -n monitoring svc/kube-prometheus-grafana 3000:80
```

Login: `admin` / password in [helm/kube-prometheus-values.yaml](../helm/kube-prometheus-values.yaml). Imports: [grafana/README.md](../grafana/README.md).

**More:** [PROMETHEUS-METRICS-LAB.md](PROMETHEUS-METRICS-LAB.md).

---

## Phase H — Argo rollback drill (only if Argo installed)

**More:** [GITOPS-ROLLBACK-DRILL.md](GITOPS-ROLLBACK-DRILL.md), [GITLESS-OPS-NOTES.md](GITLESS-OPS-NOTES.md).

---

## Phase I — Edit prep note files

| # | File |
|---|------|
| 1 | [RUNBOOK-TRACES.md](RUNBOOK-TRACES.md) |
| 2 | [SLO-LAB.md](SLO-LAB.md) |
| 3 | [SECURITY-NOTES.md](SECURITY-NOTES.md) |
| 4 | [MENTOR-QUESTIONS.md](MENTOR-QUESTIONS.md) |

Optional narrative: [WEEKLY-SESSIONS.md](WEEKLY-SESSIONS.md).

---

## Phase J — MCP on your laptop (no Kubernetes)

**Goal:** Cursor can call tools **`echo`** and **`add`** on this repo’s server. **No Qwen inside `main.py`** — see [MCP.md](MCP.md) vs **LM Studio**.

```bash
cd mcp-server
./verify.sh
```

Add the MCP JSON in **Cursor Settings → MCP** so **Cursor** starts `main.py` (you usually **do not** leave `python main.py` running in a terminal). **What to do after it connects:** [MCP.md — After you wired Cursor](MCP.md#after-you-wired-cursor-what-to-do-next).

---

## Phase K — One course smoke (optional)

[COURSE-TOOLS-SMOKE.md](COURSE-TOOLS-SMOKE.md), [VERSION-PINS.md](VERSION-PINS.md).

---

## Phase L — Optional extras

| Topic | Doc |
|------|-----|
| TLS | [TLS-CERT-MANAGER-LAB.md](TLS-CERT-MANAGER-LAB.md) |
| Phoenix | [PHOENIX-OPENINFERENCE.md](PHOENIX-OPENINFERENCE.md) |
| NetworkPolicy | [manifests/apps/networkpolicy-sample.yaml](../manifests/apps/networkpolicy-sample.yaml) |

---

## Enough for the course?

Phases **B–C** + **F–G** + **J** = solid baseline. **D–E–H** if you want GitOps practice. **K–L** optional.

---

## Other docs (reference only)

| Topic | Doc |
|------|-----|
| kind / metrics / ingress | [KIND-NOTES.md](KIND-NOTES.md) |
| Prometheus / Grafana quirks | [PROMETHEUS-METRICS-LAB.md](PROMETHEUS-METRICS-LAB.md) |
| Argo details | [ARGOCD.md](ARGOCD.md) |
| Old filename → use Phase E | [AFTER-ARGOCD-SYNC.md](AFTER-ARGOCD-SYNC.md) |
