# After Argo CD syncs the lab apps — step by step

Follow **in order**. Skip a step only if you have already completed it and noted the result.

**Assumptions:** kind cluster is up, `install-platform` (or equivalent) ran, Argo CD is installed, Applications `aire-prep-apps` and `aire-prep-observability` exist and use your Git repo. Namespace for workloads: `aire-prep`. Monitoring stack release name: `kube-prometheus` in `monitoring`.

---

## Step 1 — Confirm Argo CD state

**Action**

1. Port-forward Argo CD (if not already):

   ```bash
   kubectl port-forward svc/argocd-server -n argocd 8080:443
   ```

2. Open `https://localhost:8080`, log in as `admin` (password from [ARGOCD.md](ARGOCD.md)).

3. Open each Application (`aire-prep-apps`, `aire-prep-observability`).

**Expected:** Status **Synced** and **Healthy** (or **Progressing** briefly after a change, then Healthy).

**If Unhealthy:** click the app → **APP CONDITIONS** / failed resources → fix (common: `fake-llm` image missing → run `make load-fake-llm` on the machine that runs Docker/kind, then **Refresh** in Argo).

---

## Step 2 — Confirm pods in `aire-prep`

**Action**

```bash
kubectl get pods,svc,ingress -n aire-prep
```

**Expected:** `whoami`, `fake-llm`, `otel-collector`, `jaeger` pods **Running**; Services and Ingresses present.

---

## Step 3 — Confirm HTTP from the host (`/etc/hosts`)

**Action**

1. Ensure these lines exist (macOS/Linux):

   ```text
   127.0.0.1 whoami.aire-prep.local fake-llm.aire-prep.local
   ```

2. Run:

   ```bash
   curl -sS http://whoami.aire-prep.local | head
   curl -sS http://fake-llm.aire-prep.local/health
   ```

**Expected:** whoami returns pod/host text; health returns JSON `{"status":"ok"}`.

---

## Step 4 — Generate traffic on the “LLM” stub

**Action**

```bash
curl -sS -X POST http://fake-llm.aire-prep.local/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"model":"fake","messages":[{"role":"user","content":"hi"}]}'
```

**Expected:** JSON with a fake completion (and `lab_meta` with timing fields).

Repeat 3–5 times (needed for Grafana later).

---

## Step 5 — Traces in Jaeger

**Action**

1. In a **second** terminal:

   ```bash
   kubectl port-forward svc/jaeger 16686:16686 -n aire-prep
   ```

2. Open `http://localhost:16686`.

3. **Search** → Service = `fake-llm` (or leave empty and search **Last 15 minutes**).

4. Open a trace; confirm spans for the HTTP request.

**Expected:** At least one trace after Step 4 (if `OTEL_EXPORTER_OTLP_ENDPOINT` is set on `fake-llm`, which the lab Deployment does).

**If no traces:** check `kubectl logs deploy/fake-llm -n aire-prep` and `kubectl logs deploy/otel-collector -n aire-prep`.

---

## Step 6 — Grafana (metrics + simple panels)

**Action**

1. Confirm Service name (adjust if yours differs):

   ```bash
   kubectl get svc -n monitoring | grep grafana
   ```

   With release `kube-prometheus`, it is usually `kube-prometheus-grafana`.

2. Port-forward:

   ```bash
   kubectl port-forward -n monitoring svc/kube-prometheus-grafana 3000:80
   ```

3. Open `http://localhost:3000`.

4. Log in: user **`admin`**, password from [helm/kube-prometheus-values.yaml](../helm/kube-prometheus-values.yaml) (`changeme-prep-only` unless you changed it).

5. **Explore** → Prometheus datasource → run a test query, e.g.:

   ```promql
   up{job="kubelet"}
   ```

6. Create a **new dashboard** with **three** panels (prep goal):

   - Request rate or traffic (see [PROMETHEUS-METRICS-LAB.md](PROMETHEUS-METRICS-LAB.md): apps do not export `http_requests_total`; use **ingress-nginx** metrics after `make install-ingress`, or CPU/restarts as a stand-in).
   - Latency or duration (ingress histogram if available).
   - Error rate or non-2xx (ingress status codes if available, or pod readiness as a prep proxy).

**Expected:** Three saved panels you can reopen later. If HTTP metrics are empty, read [PROMETHEUS-METRICS-LAB.md](PROMETHEUS-METRICS-LAB.md) before assuming Prometheus ignores namespaces.

**Note:** Re-run `make install-ingress` after pulling the repo if you need ingress metrics + ServiceMonitor (values enable `controller.metrics` + `serviceMonitor`).

---

## Step 7 — GitOps drill (rollback + audit thought)

**Action**

1. Change something small in Git (e.g. a label on `whoami` Deployment in `manifests/apps/whoami/deployment.yaml`), commit, push, wait for Argo auto-sync (or **Sync** manually).

2. In Argo UI: **History** → **Rollback** one revision.

3. Write 3–5 bullets in [GITLESS-OPS-NOTES.md](GITLESS-OPS-NOTES.md): what must stay in Git for audit if AI agents proposed YAML changes.

**Expected:** You have performed at least one rollback and captured notes.

---

## Step 8 — Fill the prep templates (short documents)

**Action** (one session or split across days)

| File | What to do |
|------|------------|
| [RUNBOOK-TRACES.md](RUNBOOK-TRACES.md) | Paste commands you actually used for Jaeger + logs. |
| [SLO-LAB.md](SLO-LAB.md) | Run `curl`/`hey`, record p95 or rough latency + one draft SLO sentence. |
| [SECURITY-NOTES.md](SECURITY-NOTES.md) | Answer the checklist tables (even briefly). |
| [MENTOR-QUESTIONS.md](MENTOR-QUESTIONS.md) | List 5–7 questions before the first course day. |

---

## Step 9 — Local MCP (no cluster)

**Action**

1. Follow [MCP.md](MCP.md): venv, `pip install`, run `mcp-server/main.py`, attach to your MCP client.

2. Call tools `echo` and `add` once each.

**Expected:** Client shows tool results; you understand stdio MCP flow before cluster agent topics on the course.

---

## Step 10 — Course stack smoke tests (optional, time-boxed)

**Action**

1. Open [COURSE-TOOLS-SMOKE.md](COURSE-TOOLS-SMOKE.md).

2. Pick **one** tool (e.g. Agent Gateway or Kagent). Spend **≤ 2 hours**: install per upstream README + one hello scenario.

3. Fill the template row (version, commands, failure notes).

**Expected:** Honest notes even if you only get partway; pin versions in [VERSION-PINS.md](VERSION-PINS.md).

---

## Step 11 — Optional: TLS with cert-manager

**Action** (if you have not done TLS yet)

1. Confirm cert-manager pods: `kubectl get pods -n cert-manager`.

2. Add a ClusterIssuer (e.g. self-signed for lab) and a `Certificate` for your ingress host, or follow a minimal cert-manager tutorial.

**Expected:** You have seen a Certificate reach `Ready` once (prep for gateway/TLS topics).

---

## What comes after this doc

- **Phoenix / OpenInference:** [PHOENIX-OPENINFERENCE.md](PHOENIX-OPENINFERENCE.md) when you want eval-oriented UI.
- **Weekly narrative:** [WEEKLY-SESSIONS.md](WEEKLY-SESSIONS.md) maps these steps to the 4-week prep story.

When Steps 1–8 are done, you are in good shape for the observability + GitOps parts of the course; Steps 9–10 align with MCP / agent gateway weeks.
