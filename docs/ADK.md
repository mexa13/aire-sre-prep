# ADK smoke (Google Agent Development Kit — Python)

**ADK** is Google’s **Agent Development Kit** for building agents with tools, models, and optional web UI. It is **not** tied to this repo’s kind cluster: you run it on your laptop (or any machine with Python and network access to your chosen model API).

Use this doc for the **ADK** row in [COURSE-TOOLS-SMOKE.md](COURSE-TOOLS-SMOKE.md).

**Official:** [adk-python](https://github.com/google/adk-python) · [Python quickstart](https://google.github.io/adk-docs/get-started/python/) · [Samples](https://github.com/google/adk-samples) · [Models for ADK agents](https://google.github.io/adk-docs/agents/models/)

Pin the `pip` package in [VERSION-PINS.md](VERSION-PINS.md) after a successful smoke (`pip show google-adk`).

---

## 0) Preconditions

- **Python 3.10+** (3.11+ matches the rest of this prep repo).
- A **Gemini API key** from [Google AI Studio](https://aistudio.google.com/app/apikey) (default quickstart path), or follow [Models for ADK agents](https://google.github.io/adk-docs/agents/models/) if you use another provider.
- **`kubectl`** on your PATH and a working kubeconfig if you use the optional **cluster inspection** `agent.py` from this repo.

---

## 1) Ordered lab (minimum smoke)

`adk create` expects **`APP_NAME` to be a valid Python identifier** (letters, digits, underscores only). Names like `prep-adk-smoke` are **rejected**; use **`prep_adk_smoke`**.

Work in a throwaway directory (example: `/tmp`) so generated files do not mix with this repo.

```bash
cd /tmp
python3 -m venv adk-smoke-venv
source adk-smoke-venv/bin/activate   # Windows: adk-smoke-venv\Scripts\activate
pip install -U pip
pip install google-adk

adk create prep_adk_smoke
# API key must live next to agent.py (inside the agent package)
echo 'GOOGLE_API_KEY="YOUR_API_KEY_HERE"' > prep_adk_smoke/.env
# edit prep_adk_smoke/.env and replace the placeholder with your real key
```

### 1a) Optional — kubectl cluster inspection agent

This repo ships an example agent with **kubectl-backed tools** (nodes, workloads, events, logs, **node metrics** via `kubectl top nodes`, **Ingress/Services/Endpoints** for URL debugging):

- Source: [examples/prep_adk_smoke/agent.py](../examples/prep_adk_smoke/agent.py)

After `adk create prep_adk_smoke`, **overwrite** the generated `agent.py`:

```bash
# from the root of your clone of aire-sre-prep
cp examples/prep_adk_smoke/agent.py /tmp/prep_adk_smoke/agent.py
```

Then run the agent **from the parent directory** of `prep_adk_smoke/`:

```bash
cd /tmp
adk run prep_adk_smoke
```

**What you want:** the CLI session starts, you can send a message, and the agent responds (using the model in `agent.py`, e.g. `gemini-2.5-flash`).

**Optional — browser UI:** same parent directory as `adk run` (here **`/tmp`** — the folder that **contains** `prep_adk_smoke/`):

```bash
cd /tmp
adk web --port 8000
```

Open `http://localhost:8000`, select **`prep_adk_smoke`**, chat once. If the UI says **no agents found**, you are almost certainly in the wrong directory: use the parent of `prep_adk_smoke/`, and prefer `adk web` **without** passing the agent folder as the only path argument (see [adk-docs discussion](https://github.com/google/adk-docs/issues/817)). ADK Web is **dev-only** (see upstream caution).

**Without the optional copy:** keep the generated `agent.py` and follow the [Python quickstart](https://google.github.io/adk-docs/get-started/python/) tool example if you only need a minimal tool-calling smoke.

### Example prompts

Paste these into **`adk run`** or the **`adk web`** chat (same wording works in both).

**Generic smoke** (default generated `agent.py`, no kubectl tools):

- `Explain what a Kubernetes Deployment is in two sentences.`
- `Summarize the difference between a Pod and a Deployment.`

**Cluster inspection** (only after you copied [examples/prep_adk_smoke/agent.py](../examples/prep_adk_smoke/agent.py) over `prep_adk_smoke/agent.py`):

- `What kubectl context am I using? What is my default namespace?`
- `List all nodes and their status.`
- `Show node CPU and memory usage with kubectl top.`
- `List pods, deployments, and services in namespace aire-prep.`
- `Show recent events in namespace aire-prep and highlight anything that looks like an error.`
- `Show ingress, services, and endpoints in namespace aire-prep — I want to debug why http://whoami.aire-prep.local might not work.`
- `List workloads in namespace kagent.`
- `Show ingress, services, and endpoints in namespace ingress-nginx.`
- `Describe pod <pod-name> in namespace aire-prep` (replace `<pod-name>` with a real name from `kubectl get pods -n aire-prep`).
- `Fetch the last 200 lines of logs for pod <pod-name> in namespace aire-prep.`

The agent should call tools instead of inventing cluster state. If it answers without running tools, ask explicitly: `Use your kubectl tools to show …`.

---

## 2) Success criteria (course prep)

| Check | Pass |
|--------|------|
| `pip show google-adk` | Version recorded in VERSION-PINS.md |
| `adk run prep_adk_smoke` | At least one turn completes without auth/model errors |
| Notes | You know where **`.env`** / API key lives and default model id in `agent.py` |

---

## 3) Troubleshooting

| Symptom | Likely fix |
|---------|------------|
| `Invalid app name ... must be a valid identifier` | Use **underscores**, e.g. `prep_adk_smoke`, not `prep-adk-smoke`. |
| `GOOGLE_API_KEY` / auth errors | Fix `.env` in **`prep_adk_smoke/`** (same directory as `agent.py`), no stray quotes if your shell already wraps values. |
| Model not found / wrong name | Align `model=` in `agent.py` with [supported Gemini ids](https://google.github.io/adk-docs/agents/models/) or your provider’s doc. |
| `adk: command not found` | Activate the venv where you ran `pip install google-adk`. |
| `adk web` empty agent list | Run **`adk web`** from the **parent** of `prep_adk_smoke/` (same cwd as **`adk run prep_adk_smoke`**). Do not pass `prep_adk_smoke` as the only path argument unless docs for your version say otherwise. |
| `adk run` fails from inside agent dir | **`cd ..`** to the parent, then `adk run prep_adk_smoke`. |
| `kubectl top` errors | **metrics-server** must be installed (this lab: `make install-platform`). |

---

## 4) Relation to other Phase K tools

- **kagent / kmcp / MCP lab:** in-cluster agents and MCP — different stack from ADK CLI.
- **A2A (next in the smoke table):** protocol-level inter-agent comms — complementary, not a replacement for ADK.

When ADK smoke is done, fill the **ADK (copy block)** in [COURSE-TOOLS-SMOKE.md](COURSE-TOOLS-SMOKE.md) and optionally move to **A2A** in the same file.
