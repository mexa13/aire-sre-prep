# A2A smoke (Agent2Agent protocol)

**A2A (Agent2Agent)** is an open protocol for **agents talking to agents** across frameworks and deployments — discovery, tasks, streaming — without exposing each agent’s internal tools or memory. Transport is typically **JSON-RPC 2.0 over HTTP(S)**. **Agent Cards** advertise capabilities and connection details.

Use this doc for the **A2A** row in [COURSE-TOOLS-SMOKE.md](COURSE-TOOLS-SMOKE.md).

**Official:** [A2A spec repo](https://github.com/a2aproject/A2A) · [Documentation site](https://a2a-protocol.org) · [Specification](https://a2a-protocol.org/latest/specification/) · [Python SDK (a2a-sdk)](https://github.com/a2aproject/a2a-python) · [Samples](https://github.com/a2aproject/a2a-samples) · [Inspector (optional)](https://github.com/a2aproject/a2a-inspector)

Pin what you ran (sample path, `a2a-sdk` version, git commit of `a2a-samples`) in [VERSION-PINS.md](VERSION-PINS.md).

---

## 0) Preconditions

- **Python 3.10+**
- **[uv](https://docs.astral.sh/uv/)** (recommended by upstream samples) or adapt installs with `pip` per each sample’s `pyproject.toml`
- **Git** (clone `a2a-samples` outside this repo, e.g. under `/tmp`)

---

## 1) What to internalize (one-minute mental model)

| Idea | Takeaway |
|------|----------|
| **vs MCP** | MCP exposes **tools** to a client; A2A connects **peer agents** (opaque apps) for collaboration. They complement each other (see [A2A README](https://github.com/a2aproject/A2A)). |
| **Agent Card** | Machine-readable **discovery** document: who the agent is, skills, endpoints. |
| **Tasks** | Long-running work is modeled with a **task lifecycle** (create, update, complete) rather than a single fire-and-forget HTTP call. |
| **Transport** | **JSON-RPC 2.0** over HTTP(S); streaming and push notifications exist in the spec. |

Skim the [protocol overview](https://a2a-protocol.org/latest/topics/what-is-a2a/) (or current equivalent on a2a-protocol.org) once before running samples.

---

## 2) Ordered lab (minimum smoke — Hello World)

Upstream documents this path in [a2a-python — Examples — Helloworld](https://github.com/a2aproject/a2a-python#helloworld-example).

```bash
cd /tmp
git clone https://github.com/a2aproject/a2a-samples.git
cd a2a-samples/samples/python/agents/helloworld
uv run .
```

In a **second terminal** (same directory after `cd`):

```bash
cd /tmp/a2a-samples/samples/python/agents/helloworld
uv run test_client.py
```

**What you want:** the server stays up; the client completes without connection errors and exercises the A2A flow (exact log text varies by SDK version).

**Optional validation** (from the sample README): generic A2A CLI host under `samples/python/hosts/cli` — follow paths in [helloworld README](https://github.com/a2aproject/a2a-samples/blob/main/samples/python/agents/helloworld/README.md).

**Optional UI:** [a2a-inspector](https://github.com/a2aproject/a2a-inspector) to inspect an A2A-enabled agent URL.

---

## 3) Success criteria (course prep)

| Check | Pass |
|--------|------|
| You can state in one sentence what an **Agent Card** is for. |
| You ran **one** official sample end-to-end (Hello World server + client above). |
| `VERSION-PINS.md` | Note `a2a-sdk` version if you installed it separately, plus **commit** or date of `a2a-samples` clone. |

---

## 4) Troubleshooting

| Symptom | Likely fix |
|---------|------------|
| `uv: command not found` | Install [uv](https://docs.astral.sh/uv/getting-started/installation/) or use `pip` following the sample’s `pyproject.toml` / docs. |
| Port already in use | Stop another process on the sample’s port or change the sample config per upstream docs. |
| Client cannot reach server | Run both processes from the paths above; confirm the server log shows the listening URL. |

---

## 5) Security note (prep)

Treat remote Agent Cards and task payloads as **untrusted input** (prompt injection, malicious metadata). See the disclaimer in [a2a-samples README](https://github.com/a2aproject/a2a-samples/blob/main/README.md). Align with [SECURITY-NOTES.md](SECURITY-NOTES.md) for your own notes.

---

## 6) Relation to other Phase K tools

- **ADK:** build agents locally; A2A is how **those agents interoperate** with others at the wire level.
- **MCP / kagent:** different planes — MCP for tools, kagent for in-cluster agents; A2A is **agent-to-agent** protocol.

Previous step in this prep track: [ADK.md](ADK.md).
