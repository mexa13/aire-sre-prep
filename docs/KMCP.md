# kmcp + MCP + kagent (prep lab — one connected story)

**What `kmcp` is (the course tool):** a **CLI and workflow** around **MCP** from the kagent ecosystem — scaffold servers (Python/Go), run locally, build images, optionally deploy a controller to Kubernetes. For this repo’s Phase K you **do not** need the kmcp controller in-cluster.

**What this document is:** a **single ordered lab** that ties together **(1)** this repo’s MCP, **(2)** the kmcp scaffold, and **(3)** kagent — with **real hostnames**, **namespaces**, and **what you should see** after each step.

Also use: [MCP.md](MCP.md) (stdio lab), [KAGENT.md](KAGENT.md) (install kagent), [KIND-NOTES.md](KIND-NOTES.md#lab-hostnames-ingress) (hosts table), [COURSE-TOOLS-SMOKE.md](COURSE-TOOLS-SMOKE.md) (full MCP Python probe). Pin versions in [VERSION-PINS.md](VERSION-PINS.md).

Upstream reference (details change by release): [kagent.dev/docs/kmcp](https://kagent.dev/docs/kmcp)

---

## 0) Preconditions (must be true before the ordered steps)

| Check | Command / note |
|--------|------------------|
| Context | `kubectl config use-context kind-aire-prep` |
| Lab cluster | At least [START-HERE.md](START-HERE.md) **Phase B–C** (platform + sample apps). **MCP in cluster:** `kubectl apply -f manifests/mcp/mcp-server.yaml` (if not already applied). |
| kagent | [KAGENT.md](KAGENT.md) — Argo apps synced, pods `Running` in namespace `kagent`. |
| Hostnames | `/etc/hosts` includes the line from [KIND-NOTES.md](KIND-NOTES.md#lab-hostnames-ingress) (`mcp.aire-prep.local`, `kagent.aire-prep.local`, …). |

**Running resources this lab assumes:**

| Namespace | Workload (examples) | Role |
|-----------|---------------------|------|
| `aire-prep` | `Deployment/mcp-server`, `Service/mcp-server` port **8081** | Lab **HTTP MCP** (`echo`, `add`) at path **`/mcp`**. |
| `kagent` | UI + controllers | Where you attach **remote MCP** and run **agents**. |

---

## 1) How traffic flows (so steps are not “in a vacuum”)

```text
┌─────────────────────────────────────────────────────────────────────────┐
│ Your Mac                                                                 │
│  Cursor ──stdio──► mcp-server/main.py     (track A — [MCP.md](MCP.md))   │
│  Cursor ──stdio──► prep-kmcp-smoke (uv)   (track B — kmcp scaffold)      │
│  Browser ─────────► http://kagent.aire-prep.local  (kagent UI)            │
│  Browser/curl ────► http://mcp.aire-prep.local/mcp  (needs MCP client!) │
└─────────────────────────────────────────────────────────────────────────┘
                                      │
                                      │ ingress :80
                                      ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ kind cluster (aire-prep)                                                 │
│  Ingress ──► Service/mcp-server:8081 ──► Pod (FastMCP streamable-http)   │
│  kagent pods ──DNS──► mcp-server.aire-prep.svc.cluster.local:8081/mcp   │
│       (this URL is what you register IN kagent — not the public host)    │
└─────────────────────────────────────────────────────────────────────────┘
```

**Three tracks (all MCP, different jobs):**

| Track | What | Tools | Typical entry |
|-------|------|--------|----------------|
| **A — Lab stdio** | Repo `mcp-server/` on Mac | `echo`, `add` | Cursor `aire-prep-lab` → [MCP.md](MCP.md) |
| **B — kmcp scaffold** | `kmcp init` project on Mac | kmcp template tools | Cursor `prep-kmcp-smoke` → §4 |
| **C — Lab HTTP** | Pod in `aire-prep` | same `echo`, `add` as A | `http://mcp.aire-prep.local/mcp` from **MCP clients**; **in-cluster** URL below for **kagent** |

**kmcp is not “merged” into Agent Gateway UI:** AGW UI lists **cluster** backends like `aire-prep/mcp-server`. Your **prep-kmcp-smoke** project lives on the laptop — different artifact.

---

## 2) Ordered lab — do this sequence

### Step 1 — Lab MCP over stdio (baseline)

Do [MCP.md](MCP.md) **Phase J**: Cursor MCP `aire-prep-lab` → tools **`echo`** / **`add`**.

**Result:** you can call `echo`/`add` from Cursor; proves MCP tooling on the host.

---

### Step 2 — kmcp CLI + scaffold (course tool “kmcp”)

```bash
curl -fsSL https://raw.githubusercontent.com/kagent-dev/kmcp/refs/heads/main/scripts/get-kmcp.sh | bash
cd /tmp   # or ~/work — avoid losing /tmp on reboot
kmcp init python prep-kmcp-smoke --non-interactive || kmcp init python prep-kmcp-smoke
cd prep-kmcp-smoke && uv sync
kmcp run --project-dir .
```

In MCP Inspector: STDIO, `uv`, args `run python src/main.py` → **List tools** → run sample tool.

**Result:** you proved **kmcp** packaging/run; this is **independent** of the lab `mcp-server` code.

---

### Step 3 — Optional: same scaffold in Cursor

See **§4** below (`mcp.json` with `uv run --directory …`).

**Result:** two MCP servers in Cursor — `aire-prep-lab` (lab) and `prep-kmcp-smoke` (kmcp).

---

### Step 4 — Lab MCP over HTTP in the cluster (track C)

**Apply / verify:**

```bash
kubectl apply -f manifests/mcp/mcp-server.yaml
kubectl rollout status deployment/mcp-server -n aire-prep --timeout=120s
kubectl get pods,svc -n aire-prep -l app.kubernetes.io/name=mcp-server
```

**Public hostname (from your Mac, after `/etc/hosts`):**

- **`http://mcp.aire-prep.local/mcp`** — ingress → `mcp-server:8081`.

**Important:** a normal browser tab or plain `curl` often returns **`406`** or a JSON-RPC error like **`Client must accept text/event-stream`**. That means the **MCP transport** is rejecting a non-MCP client — the Deployment is usually **up**.

**Result you want here:** run the **Python streamable-http client** from [COURSE-TOOLS-SMOKE.md](COURSE-TOOLS-SMOKE.md) (Agent Gateway section): set `URL = "http://mcp.aire-prep.local/mcp"` (or `http://agw-mcp.aire-prep.local/mcp` for the gateway path). You should see **`echo`** / **`add`** in the tool list and a successful tool call.

---

### Step 5 — kagent uses the cluster lab MCP (integration)

**Goal:** an agent running **inside** `kagent` calls the **same** `echo` / `add` tools served by **`mcp-server`** in `aire-prep`, over **HTTP MCP**, without installing the kmcp controller.

**URL to register in kagent (for remote / HTTP MCP):**

```text
http://mcp-server.aire-prep.svc.cluster.local:8081/mcp
```

Use **Kubernetes Service DNS** — it resolves from kagent pods to the lab Service. Do **not** use `http://mcp.aire-prep.local/mcp` in kagent’s remote MCP field unless you know ingress/DNS works from those pods (usually you use **`.svc.cluster.local`**).

#### 5.1) Open kagent on the lab domain

1. Browser: **`http://kagent.aire-prep.local/`** (ingress in [manifests/kagent/ui-ingress.yaml](../manifests/kagent/ui-ingress.yaml)).
2. Log in if your install requires it (see [KAGENT.md](KAGENT.md)).

#### 5.2) Register the MCP server in the UI

1. Open **MCP / Servers** (exact menu label varies by kagent version; your build may use **`http://kagent.aire-prep.local/servers`**).
2. **Add** a server (type is usually **remote HTTP / streamable** — pick what matches “URL only”).
3. **Connection method:** **URL** (not Command).
4. **Server URL** (exactly):

   `http://mcp-server.aire-prep.svc.cluster.local:8081/mcp`

5. **Use Streamable HTTP:** **enabled** (checked). This lab’s `mcp-server` runs FastMCP with `transport=streamable-http` — SSE-only mode will not match the server.
6. **Connection timeout:** use **at least `30s`** (not `5s`). kagent performs MCP initialization and tool discovery; a short timeout often yields an empty tool list in the UI (**“No tools available for this MCP server.”**) even when the Service is healthy.
7. **Headers (JSON):** leave empty unless your install documents required auth headers.
8. Save. kagent should **discover** tools **`echo`** and **`add`** (same as the lab).

**Naming:** prefer a descriptive server name (e.g. `aire-prep-lab-mcp`) instead of `kmcp` — `kmcp` here is the upstream **CLI/product** name; it does not affect discovery but avoids confusion in screenshots and docs.

**If the UI still shows no tools** after a longer timeout, register the same endpoint declaratively and read controller status (often clearer than the UI):

```bash
kubectl apply -f - <<'EOF'
apiVersion: kagent.dev/v1alpha2
kind: RemoteMCPServer
metadata:
  name: aire-prep-lab-mcp
  namespace: kagent
spec:
  description: Lab FastMCP (echo, add) in aire-prep
  protocol: STREAMABLE_HTTP
  url: http://mcp-server.aire-prep.svc.cluster.local:8081/mcp
  timeout: 30s
  terminateOnClose: true
EOF

kubectl get remotemcpserver aire-prep-lab-mcp -n kagent -o yaml
```

Inspect `status.discoveredTools` (should list `echo` and `add`) and `status.conditions` (e.g. `Accepted`). If tools stay empty, check **kagent controller** logs around the same time and confirm `kubectl get pods -n aire-prep -l app.kubernetes.io/name=mcp-server` is **Running**.

**In-cluster smoke (optional):** from any pod in namespace `kagent`, the Service must resolve and accept MCP over Streamable HTTP — use the Python probe in [COURSE-TOOLS-SMOKE.md](COURSE-TOOLS-SMOKE.md) with `URL = "http://mcp-server.aire-prep.svc.cluster.local:8081/mcp"`. If that works from `kagent` but the UI stays empty, focus on timeout / kagent version / controller logs.

**If the UI has no “remote URL” field:** use the CLI from your machine (with kube access / port-forward as in kagent docs):

```bash
kagent add-mcp aire-prep-lab-http --remote http://mcp-server.aire-prep.svc.cluster.local:8081/mcp
```

(Adjust name/flags to your `kagent` CLI version — see upstream [kagent add-mcp](https://kagent.dev/docs/kagent/resources/cli/kagent-add-mcp).)

#### 5.3) Attach tools to an agent

1. In kagent UI: **Agents** → pick an agent (or create one).
2. **Tools / MCP:** attach the server you registered; enable tools **`echo`** and **`add`** (or all).
3. Save the agent.

#### 5.4) Prove it in kagent chat

Prompt examples:

- *Call MCP tool **echo** with text `kagent-via-cluster-mcp`.*
- *Use **add** with a=11 and b=31.*

**Success criteria:** the agent’s reply includes the echoed string or **42**; no connection errors to `mcp-server.aire-prep.svc.cluster.local`.

**Failure triage:**

| Symptom | Check |
|---------|--------|
| **“No tools available for this MCP server.”** | Raise UI timeout to **≥30s**; ensure **Streamable HTTP** is on and URL ends with **`/mcp`**. Then `kubectl get remotemcpserver -n kagent` + `kubectl describe remotemcpserver <name> -n kagent` — empty `discoveredTools` means discovery failed (controller logs, NetworkPolicy blocking `kagent` → `aire-prep:8081`). |
| Connection refused / timeout | `kubectl get pods -n aire-prep` — is `mcp-server` Running? |
| DNS fails | URL must be **`mcp-server.aire-prep.svc.cluster.local`** (not a typo). |
| 403 / auth | kagent version-specific MCP auth — see upstream docs. |

---

### Step 6 — Optional: Cursor talks **to kagent** over MCP (reverse direction)

kagent can expose **agents** as an MCP server (Streamable HTTP). See [Using Kagent agents via MCP](https://kagent.dev/docs/kagent/examples/agents-mcp).

Typical pattern: `kubectl port-forward -n kagent svc/kagent-ui 8083:8080` (adjust ports to your install), then in Cursor `mcpServers` use `"url": "http://localhost:8083/mcp"` — tools like **`list_agents`** / **`invoke_agent`**.

**Result:** Cursor orchestrates kagent agents as tools — different from Step 5, but completes the picture.

---

## 3) Domain quick reference (this lab)

| URL | Who uses it | Purpose |
|-----|----------------|----------|
| `http://kagent.aire-prep.local/` | You (browser) | kagent **UI** — register MCP (Step 5), manage agents. |
| `http://mcp.aire-prep.local/mcp` | MCP clients on Mac | Lab HTTP MCP via **ingress** (Step 4 probe). |
| `http://agw-mcp.aire-prep.local/mcp` | MCP clients on Mac | Same MCP via **Agent Gateway** ([smoke route](../manifests/agentgateway/smoke-mcp-via-agentgateway.yaml)). |
| `http://agw-ui.aire-prep.local/ui/` | You (browser) | AGW **read-only** view of programmed routes/backends. |
| `http://mcp-server.aire-prep.svc.cluster.local:8081/mcp` | **Pods in cluster** (kagent) | **Register this** in kagent as remote MCP (Step 5). |

---

## 4) Cursor + `prep-kmcp-smoke` (`mcp.json`)

**One-time:** `cd <project> && uv sync`

**Recommended (Cursor often ignores `cwd`):**

```json
{
  "mcpServers": {
    "prep-kmcp-smoke": {
      "command": "uv",
      "args": [
        "run",
        "--directory",
        "/tmp/prep-kmcp-smoke",
        "python",
        "src/main.py"
      ]
    }
  }
}
```

Change `/tmp/prep-kmcp-smoke` if you moved the project. If `uv` is not on PATH inside Cursor, set `"command"` to the output of `which uv`.

**Verify without Cursor:**

```bash
uv run --directory /tmp/prep-kmcp-smoke python -c "import dotenv; print('ok')"
```

**Shell fallback:** `"command": "/bin/sh", "args": ["-lc", "cd /tmp/prep-kmcp-smoke && exec uv run python src/main.py"]`

---

## 5) Prerequisites for kmcp local run

- **Docker** (for `kmcp run` image build path).
- **[uv](https://docs.astral.sh/uv/)**
- Optional: `npm install -g @modelcontextprotocol/inspector` for Inspector.

---

## 6) Evidence to write down (course notes)

- kmcp CLI version / install date.
- Screenshot or note: Step 2 Inspector tool call OK.
- Step 4: tool list line from Python probe against `mcp.aire-prep.local`.
- Step 5: kagent UI server URL + agent name + successful `echo`/`add` from chat.

---

## 7) Common issues

- **`/Users/.../src/main.py` missing:** use **`uv run --directory`** in Cursor (§4).
- **`No module named 'dotenv'`:** run **`uv sync`** in the kmcp project directory.
- **`mcp.aire-prep.local` “Not Found” / MCP errors in browser:** use **MCP client** (Step 4), not a random GET.
- **kagent cannot reach lab MCP:** use **`.svc.cluster.local`** URL (Step 5), verify both namespaces exist.

---

## 8) When you would install **kmcp in the cluster**

Only if you want the full upstream path: `kmcp deploy` + controller + `MCPServer` CRs. That is **not** required for Steps 1–5 above. See [kmcp quickstart deploy](https://kagent.dev/docs/kmcp/quickstart).
