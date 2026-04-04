# Runbook: find 5xx causes using traces (lab template)

Short path for **aire-prep** + **fake-llm** + **Jaeger**. Replace hosts if yours differ.

## Symptoms

- **What:** e.g. ingress returns **502** while backends are scaled down or crashing; or elevated **5xx** in Grafana “Non-2xx” panel.
- **When:** note time window and any Argo / rollout event.

## Quick checks

1. **Routing and endpoints**

   ```bash
   kubectl get ingress,svc,endpoints -n aire-prep
   ```

   If **Endpoints** for `fake-llm` is empty → expect **502** from ingress.

2. **Pod status and logs**

   ```bash
   kubectl get pods -n aire-prep -l app.kubernetes.io/name=fake-llm
   kubectl logs deploy/fake-llm -n aire-prep --tail=200
   ```

3. **Jaeger UI** (from [KIND-NOTES.md](KIND-NOTES.md))

   ```bash
   kubectl port-forward svc/jaeger 16686:16686 -n aire-prep
   ```

   Open `http://localhost:16686` → Search → service **`fake-llm`** (or leave open) → look for error spans or missing children after a failing request.

## Trace-guided path

1. Generate a failing request (e.g. with backends at zero, after pausing Argo per [PROMETHEUS-METRICS-LAB.md](PROMETHEUS-METRICS-LAB.md)).
2. If the request never reaches the app, Jaeger may show **no** `fake-llm` span — that is a signal the failure is **before** the workload (ingress / endpoints).
3. When spans exist, note which span has high latency or error flags; relate to **TTFT** / handler spans in the stub.

## Rollback / mitigate

- **Argo:** Application **History** → **Rollback** (see [GITOPS-ROLLBACK-DRILL.md](GITOPS-ROLLBACK-DRILL.md)).
- **kubectl:** `kubectl rollout undo deployment/fake-llm -n aire-prep`
- **Scale back up:** `kubectl scale deployment/fake-llm -n aire-prep --replicas=1` (remember Argo self-heal if not paused).

## Follow-ups

- **Alert:** Grafana panel “Non-2xx” or kube endpoint count for `fake-llm`.
- **Trace:** ensure OTLP path from `fake-llm` → collector → Jaeger stays up after incidents.
