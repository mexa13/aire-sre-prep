# Argo CD rollback drill (START-HERE Phase H)

Use this in **[START-HERE.md](START-HERE.md) Phase H — GitOps rollback drill**. The repo includes a **visible pod label** on `whoami` (`aire-prep.io/gitops-drill: step7-example`) so sync from Git is intentional.

## Flow

1. **Commit and push** your current branch (includes the drill label, or add your own tiny diff — e.g. another label on `manifests/apps/whoami/deployment.yaml`).
2. Wait until Argo marks **aire-prep-apps** Synced / Healthy (or click **Sync**).
3. In Argo UI: open **aire-prep-apps** → **History** → select the previous revision → **Rollback** (or use CLI if you prefer).
4. Confirm the cluster matches the rolled-back revision (e.g. `kubectl get deploy whoami -n aire-prep -o yaml | grep gitops-drill` — label absent if you rolled back before the commit).
5. **Forward fix:** sync again to `HEAD` when you want the drill label back.

## If rollback is blocked

- Check **App conditions** and resource sync errors.
- Temporarily set sync policy to manual if you need a clean experiment (see [PROMETHEUS-METRICS-LAB.md](PROMETHEUS-METRICS-LAB.md) Argo pause notes).
