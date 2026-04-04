# cert-manager TLS lab (optional)

Uses a **self-signed** issuer for local trust exercises only. Browsers will still warn unless you trust the CA.

## Prerequisites

- `make install-cert-manager` (or equivalent Helm install).
- Namespace `aire-prep` exists.

## Apply issuer + Certificate

```bash
kubectl apply -k manifests/cert-lab/
kubectl describe certificate fake-llm-tls -n aire-prep
kubectl get secret fake-llm-tls -n aire-prep
```

Wait until **Ready=True** on the Certificate.

## Attach TLS to the fake-llm Ingress

The HTTP-only Ingress is in `manifests/apps/fake-llm/ingress.yaml`. After the secret exists, add a **tls** block (patch or edit):

```yaml
spec:
  tls:
    - hosts:
        - fake-llm.aire-prep.local
      secretName: fake-llm-tls
```

Example one-liner patch (merge into existing Ingress):

```bash
kubectl patch ingress fake-llm -n aire-prep --type='json' \
  -p='[{"op":"add","path":"/spec/tls","value":[{"hosts":["fake-llm.aire-prep.local"],"secretName":"fake-llm-tls"}]}]'
```

Then test:

```bash
curl -vk https://fake-llm.aire-prep.local/health
```

(`-k` skips CA verification for the self-signed chain.)

## GitOps note

If **aire-prep-apps** has self-heal, commit the Ingress tls block to Git instead of patching, or expect Argo to revert manual patches.

## Cleanup

```bash
kubectl delete -k manifests/cert-lab/
kubectl patch ingress fake-llm -n aire-prep --type=json -p='[{"op":"remove","path":"/spec/tls"}]' 2>/dev/null || true
```
