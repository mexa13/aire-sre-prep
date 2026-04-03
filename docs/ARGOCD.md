# Argo CD bootstrap (prep lab)

GitOps gives you a baseline to contrast with **GitLess Ops** during the course. These steps install Argo CD into the kind cluster and register Applications that point at your fork of this repository.

## Install

```bash
helm repo add argo https://argoproj.github.io/argo-helm
helm repo update
helm upgrade --install argocd argo/argo-cd \
  -n argocd --create-namespace \
  --set server.service.type=NodePort \
  --wait --timeout 10m
```

Initial admin password:

```bash
kubectl -n argocd get secret argocd-initial-admin-secret \
  -o jsonpath='{.data.password}' | base64 -d && echo
```

Port-forward the UI (simplest on kind):

```bash
kubectl port-forward svc/argocd-server -n argocd 8080:443
# Open https://localhost:8080 — accept self-signed cert; user admin
```

## Register Applications

1. Push this repo (or your copy) to GitHub.
2. In `gitops/argocd/applications/*.yaml`, replace `mexa13/aire-sre-prep` with your path.
3. **Important:** The `fake-llm:prep` image is not built by Argo. Load it into kind before sync, or switch the Deployment to an image from a registry you control:

   ```bash
   make load-fake-llm
   ```

4. Apply:

   ```bash
   kubectl apply -f gitops/argocd/applications/app-aire-prep-observability.yaml
   kubectl apply -f gitops/argocd/applications/app-aire-prep-apps.yaml
   ```

## Exercise (week 2)

- Trigger a change in Git and watch sync.
- Use **History** → rollback one revision.
- Document how you would prove **auditability** if AI agents proposed manifest diffs outside Git (notes in [GITLESS-OPS-NOTES.md](GITLESS-OPS-NOTES.md)).
