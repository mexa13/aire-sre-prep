# Argo CD bootstrap (prep lab)

GitOps gives you a baseline to contrast with **GitLess Ops** during the course. This doc covers **what Make does not know** (password, Git repo URL, UI URL). The install itself matches the other platform charts.

## Install (recommended)

From the repo root:

```bash
make install-argocd
```

That runs `helm upgrade --install` with [helm/argocd-values.yaml](../helm/argocd-values.yaml): **Ingress** on `argocd.aire-prep.local`, **HTTP** (`configs.params.server.insecure: "true"`) so nginx can proxy without TLS to the pod. To reproduce by hand:

```bash
helm repo add argo https://argoproj.github.io/argo-helm
helm repo update
helm upgrade --install argocd argo/argo-cd \
  -n argocd --create-namespace \
  -f helm/argocd-values.yaml \
  --wait --timeout 10m
```

Initial admin password:

```bash
kubectl -n argocd get secret argocd-initial-admin-secret \
  -o jsonpath='{.data.password}' | base64 -d && echo
```

## Open the UI

1. Add **`argocd.aire-prep.local`** to `/etc/hosts` (see [KIND-NOTES.md](KIND-NOTES.md#lab-hostnames-ingress)).
2. Open **`http://argocd.aire-prep.local`** — user **`admin`**, password from the command above.

Fallback without hosts:

```bash
kubectl port-forward svc/argocd-server -n argocd 8080:80
# http://localhost:8080
```

## Register Applications

1. Push this repo (or your copy) to GitHub.
2. In `gitops/argocd/applications/*.yaml`, replace `mexa13/aire-sre-prep` with your path.
3. **Important:** The `fake-llm:prep` image is not built by Argo. Load it into kind before sync, or switch the Deployment to an image from a registry you control:

   ```bash
   make load-fake-llm
   ```

4. Register Applications:

   ```bash
   make apply-argocd-apps
   ```

   Or apply manifests one by one if you prefer.

## Next: after apps are synced

After Argo is up and apps sync, continue from **[START-HERE.md](START-HERE.md) Phase E** (verify, Jaeger, Grafana, rollback, templates, MCP, optional tools).

## Exercise (week 2)

- Trigger a change in Git and watch sync.
- Use **History** → rollback one revision.
- Document how you would prove **auditability** if AI agents proposed manifest diffs outside Git (notes in [GITLESS-OPS-NOTES.md](GITLESS-OPS-NOTES.md)).
