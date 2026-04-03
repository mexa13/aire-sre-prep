# Runbook: find 5xx causes using traces (lab template)

Fill this in during **week 3**. Keep it short; aim for copy-paste commands.

## Symptoms

- **What:** (e.g. intermittent 502 from ingress, spike in 5xx)
- **When:** (time window, deployment id)

## Quick checks

1. Ingress / service endpoints: `kubectl get ingress,svc,endpoints -n aire-prep`
2. Pod logs: `kubectl logs deploy/fake-llm -n aire-prep --tail=200`
3. Jaeger: port-forward (see [KIND-NOTES.md](KIND-NOTES.md)), filter `service.name=fake-llm`, look for error spans.

## Trace-guided path

1. Open a failing request trace id from logs or ingress.
2. Note span where latency jumps (TTFT vs downstream).
3. Record root cause hypothesis (one sentence).

## Rollback / mitigate

- Command used (e.g. `kubectl rollout undo`, Argo history rollback).

## Follow-ups

- What metric or alert would catch this earlier?
