# llm-d smoke (prep lab)

`llm-d` is a Kubernetes-focused stack for running LLM inference workloads (runtime + routing + serving components) with production-oriented concerns such as scaling, scheduling, and observability.

Use this doc when you do the **llm-d** row in `COURSE-TOOLS-SMOKE.md`.

---

## 1) What to verify first

Before install, decide your path:

- **CPU smoke path**: functional check only, usually slower.
- **GPU smoke path**: closer to real serving setup, needs compatible GPU nodes/resources.

Also pin versions in `docs/VERSION-PINS.md` (repo tag/chart/image/model id).

Use the local kind context from this repo:

```bash
kubectl config use-context kind-aire-prep
kubectl config current-context
```

---

## 2) Install llm-d (concrete quickstart path)

This is a practical path for this prep lab: **simulated accelerators + agentgateway profile**.
Below uses official defaults from the llm-d guide.

```bash
# clone and enter repo
cd /tmp
git clone https://github.com/llm-d/llm-d.git
cd llm-d

# install client dependencies used by guides (kubectl/helm/helmfile/yq/etc.)
./helpers/client-setup/install-deps.sh

# namespace used in this prep repo
export NAMESPACE=llm-d
kubectl create namespace "${NAMESPACE}" --dry-run=client -o yaml | kubectl apply -f -

# install required Gateway API + Inference Extension CRDs (must exist before helmfile apply)
cd guides/prereq/gateway-provider
./install-gateway-provider-dependencies.sh
kubectl api-resources --api-group=inference.networking.k8s.io

# install/upgrade gateway provider control plane (preferred self-hosted path)
# IMPORTANT for this repo: if agentgateway already exists in kind-aire-prep, SKIP this step.
# check first:
kubectl get gatewayclass agentgateway
kubectl get deploy -n agentgateway-system
# only if missing:
# helmfile sync -f agentgateway.helmfile.yaml

# deploy from the simulated accelerators guide using preferred agentgateway profile
cd ../../simulated-accelerators
# use sync to avoid local helm-diff plugin incompatibility with newer Helm
helmfile sync -e agentgateway -n "${NAMESPACE}"

# install HTTPRoute (route name: llm-d-sim)
kubectl apply -f httproute.yaml -n "${NAMESPACE}"
```

Notes:
- Namespace creation **alone** creates no workloads.
- Pods/services appear only after `helmfile apply`.
- `llm-d-deployer` is deprecated; prefer current `llm-d` + `llm-d-infra` flow.
- If `helmfile apply` fails with `no matches for kind "InferencePool"`, run the CRD installer above and retry.
- If `agentgateway.helmfile.yaml` fails with `exists and cannot be imported into the current release`, your cluster already has agentgateway resources managed elsewhere — do not reinstall control plane, reuse existing one.
- If `helm diff` fails with `if any flags in the group [validate dry-run] are set`, run `helmfile sync ...` instead of `helmfile apply ...`.

---

## 3) Readiness checks (after install)

```bash
kubectl get pods -n "${NAMESPACE}"
kubectl get svc -n "${NAMESPACE}"
kubectl get deploy,statefulset -n "${NAMESPACE}"
helm list -n "${NAMESPACE}"
```

Expected (typical names from the guide):
- pods like `infra-sim-inference-gateway-*`, `gaie-sim-epp-*`, `ms-sim-llm-d-modelservice-*` are `Running`;
- service `infra-sim-inference-gateway-istio` exists in `${NAMESPACE}`.

If empty output:
- install step was not applied yet, or applied into a different namespace/context.
- run `kubectl config current-context` and confirm you are on the expected cluster.

---

## 4) Minimum smoke (required): direct model request

Use direct decode pod access (bypass gateway):

```bash
POD="$(kubectl -n "${NAMESPACE}" get pod -l llm-d.ai/role=decode -o jsonpath='{.items[0].metadata.name}')"
kubectl -n "${NAMESPACE}" port-forward "pod/${POD}" 18080:8000
```

In another terminal:

```bash
curl -sS http://127.0.0.1:18080/v1/models
MODEL_ID="$(curl -sS http://127.0.0.1:18080/v1/models | jq -r '.data[0].id')"
curl -sS -X POST http://127.0.0.1:18080/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d "{\"model\":\"${MODEL_ID}\",\"messages\":[{\"role\":\"user\",\"content\":\"say smoke-ok\"}]}"
```

If `jq` is missing:

```bash
MODEL_ID="$(python3 - <<'PY'
import json, urllib.request
data = json.loads(urllib.request.urlopen("http://127.0.0.1:18080/v1/models").read())
print(data["data"][0]["id"])
PY
)"
```

Required success criteria:
- response is non-empty JSON;
- completion contains generated text;
- no crash loops in `${NAMESPACE}` during the call.

---

## 4.1) Optional: gateway path via Agentgateway

This path is optional in this repo because pre-existing local Agentgateway configuration can be incompatible with llm-d `InferencePool` routing.

```bash
kubectl -n "${NAMESPACE}" get svc
kubectl -n "${NAMESPACE}" port-forward svc/infra-sim-inference-gateway 8080:80
curl -sS http://127.0.0.1:8080/v1/models
```

If gateway responds with `backend does not exist`:
- check route resolution:
  ```bash
  kubectl -n "${NAMESPACE}" get httproute llm-d-sim -o jsonpath='{range .status.parents[0].conditions[*]}{.type}{\"=\"}{.status}{\"(\"}{.reason}{\") \"}{end}{\"\\n\"}'
  ```
- if `ResolvedRefs=False(BackendNotFound)` persists on a cluster with pre-existing Agentgateway install, keep direct smoke as PASS and treat gateway wiring as environment compatibility follow-up.
- this is common when your local `aire-prep` already has Agentgateway configured for regular Service backends (for example `fake-llm`/`mcp-server` routes visible in AGW UI), but not fully compatible with llm-d `InferencePool` backend resolution.

Interpretation:
- if direct smoke passes, llm-d model serving is working in-cluster;
- only the Gateway/InferencePool integration path remains as a separate compatibility task.

To make gateway path mandatory-green, use one of these:
- run llm-d guides on a fresh kind cluster without pre-existing repo Agentgateway resources;
- or replace current local Agentgateway with the exact llm-d prereq stack/version set.
- Agentgateway UI/manual backend additions are not a primary fix for llm-d path: this guide relies on `HTTPRoute -> InferencePool` (CRD-driven), while UI usually manages regular Service backends.

---

## 5) Evidence commands (for your notes)

```bash
kubectl get pods -n "${NAMESPACE}" -o wide
kubectl describe pod -n "${NAMESPACE}" <one-inference-pod-name>
kubectl logs -n "${NAMESPACE}" <one-inference-pod-name> --since=5m
```

Capture:
- used llm-d tag/chart;
- runtime image tag;
- model id;
- CPU or GPU path and reason.

---

## 6) Common failure patterns

- **No resources in namespace**: only namespace created; llm-d install not applied.
- **Pods Pending**: node selector/toleration/resource mismatch (often GPU constraints).
- **`gaie-sim-epp` Pending with `Insufficient memory` on kind**: default EPP request can be `8Gi`, which is too high for a single local node.
  Temporary smoke workaround:
  ```bash
  kubectl -n "${NAMESPACE}" patch deploy gaie-sim-epp --type='json' -p='[
    {"op":"replace","path":"/spec/template/spec/containers/0/resources/requests/memory","value":"512Mi"},
    {"op":"replace","path":"/spec/template/spec/containers/0/resources/limits/memory","value":"1Gi"},
    {"op":"replace","path":"/spec/template/spec/containers/0/resources/requests/cpu","value":"250m"}
  ]'
  kubectl -n "${NAMESPACE}" rollout status deploy/gaie-sim-epp --timeout=180s
  ```
  Note: running `helmfile sync` again may restore chart defaults; for persistent behavior use a values override.
- **ImagePullBackOff**: wrong image tag or registry auth issue.
- **OOMKilled**: model size exceeds CPU RAM / GPU VRAM allocation.
- **404 / unknown model**: request model id does not match runtime registration.
- **Health OK but empty/failed generation**: check runtime args, model download/mount status, and logs.

