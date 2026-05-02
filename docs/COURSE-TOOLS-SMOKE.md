# Course stack smoke tests (install only)

Tools from the course announcement evolve. Prep goal: **open the official links below → install → complete the one prep task** for each tool you choose (you do **not** need every row). Pin versions in [VERSION-PINS.md](VERSION-PINS.md).

If a link breaks, search the **GitHub org/repo** name in the table — projects sometimes move docs paths.

| Tool | Official sources | One prep task (minimum) |
|------|------------------|------------------------|
| **Agent Gateway** | Repo: [github.com/agentgateway/agentgateway](https://github.com/agentgateway/agentgateway) · Docs: [agentgateway.dev](https://agentgateway.dev/) · K8s: [Agentgateway on Kubernetes](https://agentgateway.dev/docs/kubernetes/) | Follow the current **quickstart or Kubernetes install** until a single **routed request** hits a backend (or their documented hello path); note how **auth** (API key / JWT) is configured. |
| **Kagent** | Repo: [github.com/kagent-dev/kagent](https://github.com/kagent-dev/kagent) · Docs: [kagent.dev/docs](https://kagent.dev/docs) | Complete **Quick start** so an **agent runs in-cluster** and **one tool call** succeeds; list **CRDs** installed (`kubectl get crd \| grep -i kagent` or per their docs). |
| **llm-d** | Repo: [github.com/llm-d/llm-d](https://github.com/llm-d/llm-d) · Docs: [llm-d.ai](https://www.llm-d.ai/) | Run the smallest **install / demo** from current docs so **at least one inference-related workload** is `Running` (or their equivalent check); write down **GPU vs CPU** assumptions from the guide. |
| **kmcp** | Repo: [github.com/kagent-dev/kmcp](https://github.com/kagent-dev/kmcp) · Docs: [kagent.dev/docs/kmcp](https://kagent.dev/docs/kmcp) · Deploy (optional): [Deploy MCP servers](https://kagent.dev/docs/kmcp/deploy/server) | **Ordered lab:** [KMCP.md §2](KMCP.md#2-ordered-lab--do-this-sequence) (stdio MCP → kmcp scaffold → HTTP probe → **kagent UI** + `http://mcp-server.aire-prep.svc.cluster.local:8081/mcp`). No kmcp controller required. |
| **ADK** | Repo: [github.com/google/adk-python](https://github.com/google/adk-python) · Docs: [Get started (Python)](https://google.github.io/adk-docs/get-started/python/) · Samples: [google/adk-samples](https://github.com/google/adk-samples) | **Ordered lab:** [ADK.md §1](ADK.md#1-ordered-lab-minimum-smoke) — venv, `pip install google-adk`, **`adk create prep_adk_smoke`** (underscores; hyphens invalid) + **`.env`** + optional copy [examples/prep_adk_smoke/agent.py](../examples/prep_adk_smoke/agent.py) → `prep_adk_smoke/agent.py`; **`adk run prep_adk_smoke`**; optional **`adk web`**. |
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
  # if auth header is required:
  export OPENAI_API_KEY="<lm-studio-token-or-placeholder>"
  kubectl create secret generic kagent-openai -n kagent \
    --from-literal OPENAI_API_KEY="$OPENAI_API_KEY" \
    --dry-run=client -o yaml | kubectl apply -f -

Final smoke commands:
  kubectl get applications.argoproj.io -n argocd | grep kagent
  kubectl get pods -n kagent
  kubectl get modelconfigs.kagent.dev -n kagent default-model-config -o yaml | grep -E "model:|baseUrl:"
  kubectl run lmstudio-models-probe --rm -it --restart=Never -n kagent --image=curlimages/curl:8.7.1 -- \
    sh -lc 'curl -sS -H "Authorization: Bearer '"$OPENAI_API_KEY"'" http://192.168.18.43:1234/v1/models'
  kagent invoke -t "What Helm charts are in my cluster?" --agent helm-agent
  # optional resilience test:
  kagent invoke -t "Delete one existing pod whose name starts with fake-llm- in namespace aire-prep, then verify replacement pod is Running. Show before/after names." --agent k8s-agent

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

## llm-d (completed smoke template for this repo)

`llm-d` is a Kubernetes-focused stack for running/serving LLM inference workloads (router + runtime + model serving), with production concerns like scheduling, autoscaling, and observability.
Full step-by-step guide for this repo: [LLM-D.md](LLM-D.md).

```text
Tool: llm-d
Version / chart / image:
  Repo commit/tag: <pin exact tag from llm-d docs you used>
  Runtime image(s): <vllm/sglang/other image tags used in your install>

Install command(s):
  # 1) follow the official quickstart/install from:
  #    https://github.com/llm-d/llm-d
  #    https://www.llm-d.ai/
  #
  # 2) keep all resources in dedicated namespace
  kubectl create namespace llm-d --dry-run=client -o yaml | kubectl apply -f -
  # then run llm-d install from docs (helm/kustomize/operator path) into this namespace
  # NOTE: creating namespace alone does NOT create workloads.

Readiness checks (run only AFTER llm-d install is applied):
  kubectl get pods -n llm-d
  kubectl get svc -n llm-d
  kubectl get deploy,statefulset -n llm-d
  # expected after successful install: controller + inference workload pods become Running/Ready

Single test command (minimum smoke):
  # required pass in this repo setup: direct decode pod smoke
  POD=$(kubectl -n llm-d get pod -l llm-d.ai/role=decode -o jsonpath='{.items[0].metadata.name}')
  kubectl -n llm-d port-forward "pod/${POD}" 18080:8000
  curl -sS http://127.0.0.1:18080/v1/models
  curl -sS -X POST http://127.0.0.1:18080/v1/chat/completions -H "Content-Type: application/json" \
    -d '{"model":"random","messages":[{"role":"user","content":"say smoke-ok"}]}'
  # optional advanced check: gateway path via infra-sim-inference-gateway service

Evidence commands (write output into your notes):
  kubectl get pods -n llm-d -o wide
  kubectl describe pod -n llm-d <one-inference-pod-name>
  kubectl logs -n llm-d <one-inference-pod-name> --since=5m

CPU/GPU assumption note (required for this course prep):
  - CPU path: slower, often for functional smoke only.
  - GPU path: preferred for realistic latency/throughput; document GPU type/count and requested resources.
  - Record which path you used and why.

Failure / follow-up:
  - Pods Pending: node selector/toleration/GPU resource mismatch (no compatible node).
  - ImagePullBackOff: registry/auth/image tag mismatch.
  - OOMKilled: model too large for allocated memory/VRAM.
  - 404/invalid model in inference call: wrong model id vs runtime registration.
  - Health OK but no token output: check provider/runtime args and model mount/download status.
```

---

## kmcp (completed smoke template for this repo)

Full step-by-step guide: [KMCP.md](KMCP.md).

```text
Tool: kmcp
Version / chart / image: (kmcp CLI from get-kmcp.sh; pin output in VERSION-PINS.md)

Install command(s):
  curl -fsSL https://raw.githubusercontent.com/kagent-dev/kmcp/refs/heads/main/scripts/get-kmcp.sh | bash
  kmcp --help

Practice (local, no cluster required):
  cd /tmp
  kmcp init python prep-kmcp-smoke --non-interactive
  cd prep-kmcp-smoke
  kmcp run --project-dir .
  # In MCP Inspector: STDIO, command uv, args: run python src/main.py; List tools → run echo

Optional headless:
  kmcp run --project-dir . --no-inspector

Single test command (minimum):
  # One successful tool invocation via Inspector (echo) on the scaffolded project

Optional integrations (see KMCP.md §2 Step 3–5):
  # Cursor prep-kmcp-smoke: KMCP.md §4 (uv run --directory …)
  # kagent + lab MCP: http://kagent.aire-prep.local → register http://mcp-server.aire-prep.svc.cluster.local:8081/mcp

Failure / follow-up:
  - Docker not running / build failures during kmcp run
  - uv or Node inspector missing per docs
  - Optional K8s deploy only if you choose full kmcp controller path (official quickstart)
```

---

## ADK (copy block)

```text
Tool: ADK (google-adk)
Version / chart / image: (pip show google-adk)
Install command(s):
  cd /tmp && python3 -m venv adk-smoke-venv && source adk-smoke-venv/bin/activate
  pip install -U pip google-adk
  adk create prep_adk_smoke
  echo 'GOOGLE_API_KEY="…"' > prep_adk_smoke/.env   # aistudio.google.com/app/apikey
  # optional: kubectl lab agent — from aire-sre-prep repo root:
  #   cp examples/prep_adk_smoke/agent.py /tmp/prep_adk_smoke/agent.py
Single test command:
  # cwd = parent of prep_adk_smoke/
  adk run prep_adk_smoke
  # optional UI: adk web --port 8000   (same parent cwd)
Failure / follow-up:
  - Invalid app name: use prep_adk_smoke (underscores), not prep-adk-smoke
  - Missing/invalid GOOGLE_API_KEY in prep_adk_smoke/.env
  - adk run / adk web from wrong cwd (parent of agent folder; adk web often without agent subpath)
Lab doc: docs/ADK.md
Example agent: examples/prep_adk_smoke/agent.py
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
