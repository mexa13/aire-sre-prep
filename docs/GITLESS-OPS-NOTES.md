# GitLess Ops — prep notes

**Intent:** capture how AI-assisted change might bypass the classic “PR + review + CI” loop, and what **evidence** you still need for production.

## Questions to answer before the course

1. Which changes must still land in Git for audit (Terraform, K8s, policy)?  
2. Where would you store **signed prompts / agent plans** if not in Git?  
3. How do you detect **drift** between cluster state and declared intent without full GitOps?  
4. What CI checks remain non-negotiable (security scans, policy tests)?  

## Audit stance for this lab (example answers — refine for your org)

- **Must stay in Git for audit:** Kubernetes manifests in `manifests/` and `gitops/argocd/applications/`; Helm values under `helm/`; any change that affects ingress, TLS, or workload identity. Terraform / cloud IAM for real prod would be the same class of artifact.
- **Prompts / agent plans outside Git:** Store in an append-only log (SIEM, object storage with versioning) with **correlation IDs** matching OpenTelemetry trace IDs; treat like security-sensitive operational records, not like app source.
- **Drift without full GitOps:** Compare `kubectl get` (or `argocd app diff`) to rendered manifests; schedule periodic **drift detection** jobs; for AI-proposed edits, require a machine-readable “intent manifest” that can be diffed.
- **Non-negotiable CI:** Image scan (Trivy/Grype), signed commits or required reviewers on default branch, policy-as-code (Kyverno/OPA) in cluster for anything touching `aire-prep` or prod namespaces.

## Your stance (fill in)

- **Comfortable automating:** (e.g. lint/format, test generation, doc drafts, Helm value suggestions with CI render check)  
- **Never without human gate:** (e.g. production Argo sync, secret material, destructive Terraform)  
- **Open questions for mentor:** see [MENTOR-QUESTIONS.md](MENTOR-QUESTIONS.md)

## Rollback drill reminder

After you run [GITOPS-ROLLBACK-DRILL.md](GITOPS-ROLLBACK-DRILL.md), add one line here on what **felt** different vs a normal Git revert (speed, visibility, blast radius).

- **After drill:** _(add your note)_
