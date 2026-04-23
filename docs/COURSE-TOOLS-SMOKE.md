# Course stack smoke tests (install only)

Tools from the course announcement evolve. Prep goal: **open the official links below → install → complete the one prep task** for each tool you choose (you do **not** need every row). Pin versions in [VERSION-PINS.md](VERSION-PINS.md).

If a link breaks, search the **GitHub org/repo** name in the table — projects sometimes move docs paths.

| Tool | Official sources | One prep task (minimum) |
|------|------------------|------------------------|
| **Agent Gateway** | Repo: [github.com/agentgateway/agentgateway](https://github.com/agentgateway/agentgateway) · Docs: [agentgateway.dev](https://agentgateway.dev/) · K8s: [Agentgateway on Kubernetes](https://agentgateway.dev/docs/kubernetes/) | Follow the current **quickstart or Kubernetes install** until a single **routed request** hits a backend (or their documented hello path); note how **auth** (API key / JWT) is configured. |
| **Kagent** | Repo: [github.com/kagent-dev/kagent](https://github.com/kagent-dev/kagent) · Docs: [kagent.dev/docs](https://kagent.dev/docs) | Complete **Quick start** so an **agent runs in-cluster** and **one tool call** succeeds; list **CRDs** installed (`kubectl get crd \| grep -i kagent` or per their docs). |
| **llm-d** | Repo: [github.com/llm-d/llm-d](https://github.com/llm-d/llm-d) · Docs: [llm-d.ai](https://www.llm-d.ai/) | Run the smallest **install / demo** from current docs so **at least one inference-related workload** is `Running` (or their equivalent check); write down **GPU vs CPU** assumptions from the guide. |
| **kmcp** | Repo: [github.com/kagent-dev/kmcp](https://github.com/kagent-dev/kmcp) · Docs: [kagent.dev/docs/kmcp](https://kagent.dev/docs/kmcp) · Deploy: [Deploy MCP servers](https://kagent.dev/docs/kmcp/deploy/server) | Per quickstart: **register or deploy one MCP server** (CLI or controller) and verify **one tool/list** call from their documented test path. |
| **ADK** | Repo: [github.com/google/adk-python](https://github.com/google/adk-python) · Docs: [Get started (Python)](https://google.github.io/adk-docs/get-started/python/) · Samples: [google/adk-samples](https://github.com/google/adk-samples) | `pip install google-adk`, run **`adk create`** + **`adk run`** on the generated agent (or follow the doc’s hello path); note **API key / model** requirement. |
| **A2A** | Repo: [github.com/a2aproject/A2A](https://github.com/a2aproject/A2A) (spec + samples; start from README **Documentation** links) | Read **protocol overview** + run or trace **one official sample** from the repo (e.g. under `samples/` if present) or the path linked from README; note **JSON-RPC / Agent Card** takeaway in your notes. |

---

## Kagent (completed smoke on this repo)

```text
Tool: Kagent
Version / chart / image: chart kagent=v0.8.6, chart kagent-crds=v0.8.6

Install command(s):
  kubectl apply -f gitops/argocd/applications/app-kagent-CRD-helm.yaml
  kubectl apply -f gitops/argocd/applications/app-kagent-helm.yaml

  export OPENAI_API_KEY="<your-openai-key>"
  kubectl create secret generic kagent-openai -n kagent \
    --from-literal OPENAI_API_KEY="$OPENAI_API_KEY" \
    --dry-run=client -o yaml | kubectl apply -f -

  kubectl get applications.argoproj.io -n argocd | grep kagent
  kubectl get pods -n kagent

  # UI via domain
  make apply-kagent-smokes
  # add kagent.aire-prep.local to /etc/hosts
  # open http://kagent.aire-prep.local

CRDs installed:
  kubectl get crd | grep -i kagent

Single test command (one tool call):
  kagent invoke -t "What Helm charts are in my cluster?" --agent helm-agent
  # expected: response includes Helm tool output (release/chart list)

LM Studio option (OpenAI-compatible):
  kubectl apply -f manifests/kagent/modelconfig-lmstudio.yaml
  # then choose model config kagent/lmstudio-openai in the UI

Failure / follow-up:
  - kagent pods not Ready: check kagent namespace events and controller logs.
  - Empty/failed responses: verify model provider config and API key secret.
  - For local LM Studio, ensure in-cluster reachability to host.docker.internal:1234.
```

---

## Agent Gateway (completed smoke on this repo)

```text
Tool: Agent Gateway
Version / chart / image: chart agentgateway v1.0.1, chart agentgateway-crds v1.0.1, controller image cr.agentgateway.dev/controller:v1.0.1
Install command(s):
  kubectl apply -f gitops/argocd/applications/app-agentgateway-CRD-helm.yaml
  kubectl apply -f gitops/argocd/applications/app-agentgateway-helm.yaml
  make apply-argocd-apps
  kubectl get applications.argoproj.io -n argocd
  # make apply-argocd-apps also applies Agent Gateway smoke manifests:
  # smoke-fake-llm, smoke-mcp-via-agentgateway, ui-ingress

Single test command:
  curl --resolve agw-fake-llm.aire-prep.local:80:127.0.0.1 \
    http://agw-fake-llm.aire-prep.local/health
  # expected: {"status":"ok"}

Evidence command:
  kubectl logs -n agentgateway-system deploy/agentgateway-smoke --since=5m | grep "request gateway="

Domain verification commands (MCP direct + via Agent Gateway):
  curl -i http://mcp.aire-prep.local/mcp
  curl -i http://agw-mcp.aire-prep.local/mcp
  # expected for plain curl: 406 Not Acceptable (MCP endpoint requires protocol headers/session)

Agent Gateway admin UI (domain):
  # add agw-ui.aire-prep.local to /etc/hosts (see docs/KIND-NOTES.md)
  # open:
  http://agw-ui.aire-prep.local/ui

Real MCP client smoke via domain:
  /Users/mexa/Documents/projects/NYX/aire-sre-prep/mcp-server/.venv/bin/python - <<'PY'
  import asyncio
  from mcp.client.streamable_http import streamablehttp_client
  from mcp.client.session import ClientSession

  URL = "http://agw-mcp.aire-prep.local/mcp"

  async def main():
      async with streamablehttp_client(URL, timeout=20, sse_read_timeout=60) as (r, w, _):
          async with ClientSession(r, w) as s:
              await s.initialize()
              tools = await s.list_tools()
              print("tools:", [t.name for t in tools.tools])
              print("echo:", await s.call_tool("echo", {"text": "domain-smoke-ok"}))
              print("add:", await s.call_tool("add", {"a": 21, "b": 21}))

  asyncio.run(main())
  PY

Failure / follow-up:
  - CRD sync failed with metadata.annotations too long (~256Ki kubectl last-applied annotation limit).
  - Fix: set sync option ServerSideApply=true in app-agentgateway-CRD-helm.yaml.
  - Initial route tests returned "route not found" when hostname constraints were present; using the minimal route without hostnames resolved matching in this prep setup.
  - Agent Gateway admin UI listens on localhost in the gateway pod. `manifests/agentgateway/ui-ingress.yaml` adds an in-cluster forwarder and ingress so UI is available at `http://agw-ui.aire-prep.local/ui`.
```

Files used for this smoke:
- `manifests/agentgateway/smoke-fake-llm.yaml`
- `manifests/agentgateway/ui-ingress.yaml`
- `gitops/argocd/applications/app-agentgateway-CRD-helm.yaml`
- `gitops/argocd/applications/app-agentgateway-helm.yaml`

---

## llm-d (copy block)

```text
Tool: llm-d
Version / chart / image:
Install command(s):
Single test command: (e.g. kubectl get pods / their health check)
Failure / follow-up: (GPU nodes, image pull, etc.)
```

---

## kmcp (copy block)

```text
Tool: kmcp
Version / chart / image:
Install command(s):
Single test command: (e.g. kmcp CLI or kubectl get mcp* CRs)
Failure / follow-up:
```

---

## ADK (copy block)

```text
Tool: ADK (google-adk)
Version / chart / image: (pip version)
Install command(s):
Single test command: (e.g. adk run …)
Failure / follow-up:
```

---

## A2A (copy block)

```text
Tool: A2A protocol
Version / spec / sample commit:
Commands / URL exercised:
One-sentence takeaway (Agent Card / task lifecycle):
Failure / follow-up:
```

---

## Template (generic — any other tool)

```text
Tool:
Official URL:
Version / chart / image:
Install command(s):
Single test command:
Failure / follow-up:
```

---

## Notes

- Prefer **kind load** or an **in-cluster registry** for images you build.
- If two tools both want ingress: use separate hostnames or paths and document conflicts.
- **Agent Gateway** (agentgateway) is distinct from **Kubernetes Gateway API** “gateway” tutorials — use the agentgateway.dev links above.
