# Security prep notes (LLM proxy + MCP)

Use this as a **checklist**, not a compliance pack. Example answers reflect **this prep repo** — replace for production.

## Secrets

| Item | Question | Lab / prep answer |
|------|----------|-------------------|
| API keys | Stored in **Kubernetes Secret** vs **ExternalSecrets** / Vault? | Lab uses no LLM API keys on `fake-llm`. For real keys: **Secret** + narrow RBAC; prod → **ExternalSecrets** / Vault. |
| Rotation | Who rotates, how often, how do pods pick up new mounts? | Rotate on leak; restart pods or use projected volumes / rotation operator. |
| Least privilege | Which SA can read which Secret? | Default SA in `aire-prep` should not read cluster-wide secrets; use dedicated SA + `roleRef` per workload. |

## Network

| Item | Question | Lab / prep answer |
|------|----------|-------------------|
| Blast radius | Can every pod talk to the LLM gateway, or only ingress / selected namespaces? | Today: ingress → Service → pods. Tighten with **NetworkPolicy** so only ingress-nginx namespace can reach `fake-llm` Service port. |
| NetworkPolicy | Where would you add **deny-by-default** first? | Start with `aire-prep`: default deny ingress, then allow from `ingress-nginx` only — see [manifests/apps/networkpolicy-sample.yaml](../manifests/apps/networkpolicy-sample.yaml). |

## MCP / agent auth

| Item | Question | Lab / prep answer |
|------|----------|-------------------|
| Tool exfiltration | What stops a tool from calling unintended hosts? | **stdio MCP** in [mcp-server/](../mcp-server) has no network by default; in-cluster agents need egress policy + allowlisted tool implementations. |
| Identity | How does the server trust the client (mTLS, tokens)? | Prep: OS user on same machine. Prod: **mTLS** or **signed tokens** per tool session. |
| Audit | Are tool calls logged with correlatable trace ids? | Add structured logging / OTel spans around tool dispatch; correlate with **trace_id** in gateway logs. |

## Prompt / content guards

| Item | Question | Lab / prep answer |
|------|----------|-------------------|
| Abuse | Rate limits at gateway vs app? | Prefer **ingress/gateway** first (see Grafana ingress rate panel); add app limits for cost-sensitive paths. |
| Injection | Where do you enforce **prompt guards** relative to the model provider? | Before the model call in the **gateway** or a dedicated **policy sidecar**; log blocked attempts with request id. |

## Homework — demo policy applied (lab)

**NetworkPolicy (optional):** Applied [manifests/apps/networkpolicy-sample.yaml](../manifests/apps/networkpolicy-sample.yaml) only if your CNI enforces policies (kind often does). Before apply: `kubectl get pods -n kube-system` and confirm CNI. After apply: verify `curl` from host still works via ingress; a random pod in another namespace without policy allow should not reach `fake-llm:8080`.

**Argo / Git:** Treat all changes to `manifests/` as **reviewed PRs**; avoid `kubectl edit` in prod without a ticket — aligns with audit for AI-suggested YAML.
