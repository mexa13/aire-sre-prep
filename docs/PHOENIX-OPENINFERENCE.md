# Phoenix and OpenInference (optional prep)

Goal: one **UI** where you can relate traces / spans to eval-style signals. Upstream moves quickly — treat this as orientation, not a frozen architecture.

## Option A — Phoenix locally (Docker)

Refer to the current [Arize Phoenix docs](https://docs.arize.com/phoenix) for the one-line Docker run. In prep, you can:

1. Run Phoenix on the host or in Docker Desktop.
2. Point **fake-llm** or a small Python script at Phoenix’s OTLP/HTTP endpoint (if supported in your version) **or** use the Phoenix SDK examples for a minimal experiment.

## Option B — OpenInference in cluster

Check the [OpenInference](https://github.com/Arize-ai/openinference) repositories for Helm/Kubernetes instructions. Success criterion for prep: **one span or experiment record** visible in UI.

## If blocked

Document the blocker (version, missing ARM image, auth) in your notes and move on — the course will deep-dive.
