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

## Kagent (recommended first smoke)

Use the links in the table above. **Prep goal:** follow the current **Quick start** for your environment (kind-friendly if offered). Record what you actually ran below.

**Template (fill on your machine)**

```text
Tool: Kagent
Version / chart / image: (e.g. release tag from GitHub / helm chart version)
Install command(s):
Single test command:
Failure / follow-up:
```

**Example stub (replace with your run output)**

```text
Tool: Kagent
Version / chart / image: see VERSION-PINS.md → kagent
Install command(s): (from upstream docs — often helm or kubectl apply)
Single test command: (e.g. CLI/UI agent invocation from their quickstart)
Failure / follow-up: (ARM image, CRD conflicts, LLM API key required, etc.)
```

---

## Agent Gateway (copy block if you smoke-test it)

```text
Tool: Agent Gateway
Version / chart / image:
Install command(s):
Single test command: (e.g. curl to routed endpoint with auth header)
Failure / follow-up:
```

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
