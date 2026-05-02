# Kagent smoke (prep lab)

`kagent` is a Kubernetes-native agent framework: it runs agent controllers in-cluster, lets you create agents in UI/CLI, and executes tools (kubectl/helm/kmcp etc.) from those agents.

Use this doc when you do the **Kagent** row in [COURSE-TOOLS-SMOKE.md](COURSE-TOOLS-SMOKE.md).

---

## 1) Install via Argo CD (Helm charts)

Apply Argo `Application` objects:

```bash
kubectl apply -f gitops/argocd/applications/app-kagent-CRD-helm.yaml
kubectl apply -f gitops/argocd/applications/app-kagent-helm.yaml
```

Create OpenAI key secret used by the chart:

```bash
export OPENAI_API_KEY="<your-openai-key>"
kubectl create secret generic kagent-openai -n kagent \
  --from-literal OPENAI_API_KEY="$OPENAI_API_KEY" \
  --dry-run=client -o yaml | kubectl apply -f -
```

Sync/check:

```bash
kubectl get applications.argoproj.io -n argocd | rg kagent
kubectl get pods -n kagent
```

---

## 2) Expose UI by domain

Apply ingress:

```bash
make apply-kagent-smokes
```

Add host in `/etc/hosts` (see [KIND-NOTES.md](KIND-NOTES.md#lab-hostnames-ingress)):

```text
127.0.0.1 kagent.aire-prep.local
```

Open:

```text
http://kagent.aire-prep.local
```

Fallback:

```bash
kubectl port-forward -n kagent svc/kagent-ui 8082:8080
# http://localhost:8082
```

---

## 3) Prove CRDs installed

```bash
kubectl get crd | grep -i kagent
```

Optional full count:

```bash
kubectl get crd | grep -ic kagent
```

---

## 4) Smoke: one agent + one tool call

The quick smoke is to use built-in `helm-agent` and trigger a Helm tool call.

Install CLI (if needed):

```bash
brew install kagent
```

Run:

```bash
kagent invoke -t "What Helm charts are in my cluster?" --agent helm-agent
```

Success criteria:
- Response includes chart/release data (tool output, not only generic text).
- In UI chat details, you can expand Arguments/Results for the tool execution.

---

## 5) LM Studio (OpenAI-compatible) option

Yes, you can use LM Studio instead of OpenAI cloud.

1. Start LM Studio local server (OpenAI-compatible API), usually `http://host.docker.internal:1234/v1` from in-cluster workloads.
2. Keep secret `kagent-openai` (LM Studio often accepts any placeholder key).
3. Apply:

```bash
kubectl apply -f manifests/kagent/modelconfig-lmstudio.yaml
```

Then in kagent UI, choose model config `kagent/lmstudio-openai` when creating/updating the agent.

If your LM Studio endpoint expects auth header, keep a token in the secret:

```bash
export OPENAI_API_KEY="<lm-studio-token-or-placeholder>"
kubectl create secret generic kagent-openai -n kagent \
  --from-literal OPENAI_API_KEY="$OPENAI_API_KEY" \
  --dry-run=client -o yaml | kubectl apply -f -
```

Notes:
- Replace `model` in `manifests/kagent/modelconfig-lmstudio.yaml` with exact LM Studio model ID from `/v1/models`.
- For reliable tool-use/function-calling, prefer strong instruction-tuned models. For local tests, a Qwen coder model can work, but cloud `gpt-4.1-mini` is usually more predictable for first smoke.
- `n_ctx` / context length is controlled by LM Studio model load settings, not by kagent `ModelConfig`.
- If kagent requests `qwen3.5-9b` but your loaded model id is `qwen/qwen3.5-9b`, LM Studio can auto-load a second model profile (often with default 4096 context). Always use the exact id.

---

## 6) Final smoke (LM Studio + kagent)

```bash
# 1) Argo + workloads
kubectl get applications.argoproj.io -n argocd | grep kagent
kubectl get pods -n kagent

# 2) Model config used by built-in agents
kubectl get modelconfigs.kagent.dev -n kagent default-model-config -o yaml | grep -E "model:|baseUrl:"

# 3) LM Studio reachability from cluster (with Bearer token)
export OPENAI_API_KEY="<lm-studio-token-or-placeholder>"
kubectl run lmstudio-models-probe --rm -it --restart=Never -n kagent \
  --image=curlimages/curl:8.7.1 -- \
  sh -lc 'curl -sS -H "Authorization: Bearer '"$OPENAI_API_KEY"'" http://192.168.18.43:1234/v1/models'

# 4) Chat completion probe from cluster (replace model if needed)
kubectl run lmstudio-chat-probe --rm -it --restart=Never -n kagent \
  --image=curlimages/curl:8.7.1 -- \
  sh -lc 'curl -sS -H "Authorization: Bearer '"$OPENAI_API_KEY"'" -H "Content-Type: application/json" \
  http://192.168.18.43:1234/v1/chat/completions \
  -d "{\"model\":\"qwen3.5-9b\",\"messages\":[{\"role\":\"user\",\"content\":\"say ok\"}]}"'

# 5) kagent tool call smoke
kagent invoke -t "What Helm charts are in my cluster?" --agent helm-agent
```

---

## 7) Optional resilience smoke: delete pod -> auto-recreate

Use `k8s-agent` for this test.

Prompt in kagent UI:

```text
Delete one existing pod whose name starts with fake-llm- in namespace aire-prep, then verify replacement pod is Running. Show before/after names.
```

Optional CLI equivalent:

```bash
kagent invoke -t "Delete one existing pod whose name starts with fake-llm- in namespace aire-prep, then verify replacement pod is Running. Show before/after names." --agent k8s-agent
```

Manual verification (host kubectl):

```bash
kubectl get pods -n aire-prep -l app=fake-llm -w
```

Success criteria:
- One `fake-llm` pod is deleted.
- Deployment/ReplicaSet creates a new pod automatically.
- New pod reaches `Running` state.

---

## 8) Optional: attach this lab’s HTTP MCP or use kmcp (no extra cluster install)

The repo already runs **MCP over HTTP** in `aire-prep` (`manifests/mcp/mcp-server.yaml`) — tools `echo` / `add`.

**Concrete lab steps (domains, UI order, success criteria):** [KMCP.md — §2 Step 5](KMCP.md#step-5--kagent-uses-the-cluster-lab-mcp-integration) (`http://kagent.aire-prep.local` → register `http://mcp-server.aire-prep.svc.cluster.local:8081/mcp`).

**kmcp CLI on the laptop (no kmcp controller):** same doc **§2 Steps 2–4** and **§4** (Cursor `prep-kmcp-smoke`).
