# Security prep notes (LLM proxy + MCP)

Use this as a **checklist**, not a compliance pack.

## Secrets

| Item | Question |
|------|----------|
| API keys | Stored in **Kubernetes Secret** vs **ExternalSecrets** / Vault? |
| Rotation | Who rotates, how often, how do pods pick up new mounts? |
| Least privilege | Which SA can read which Secret? |

## Network

| Item | Question |
|------|----------|
| Blast radius | Can every pod talk to the LLM gateway, or only ingress / selected namespaces? |
| NetworkPolicy | Where would you add **deny-by-default** first? (see sample in `manifests/apps/networkpolicy-sample.yaml`) |

## MCP / agent auth

| Item | Question |
|------|----------|
| Tool exfiltration | What stops a tool from calling unintended hosts? |
| Identity | How does the server trust the client (mTLS, tokens)? |
| Audit | Are tool calls logged with correlatable trace ids? |

## Prompt / content guards

| Item | Question |
|------|----------|
| Abuse | Rate limits at gateway vs app? |
| Injection | Where do you enforce **prompt guards** relative to the model provider? |

## Homework

Add one **demo policy** you actually applied (ingress annotation, gateway rule, or OPA/Gatekeeper sketch) — one paragraph in this file.
