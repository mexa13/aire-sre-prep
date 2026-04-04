# Phoenix and OpenInference (optional prep)

Goal: one **UI** where you can relate traces / spans to eval-style signals. Upstream moves quickly — treat this as orientation, not a frozen architecture.

## Option A — Phoenix locally (Docker)

Refer to the current [Arize Phoenix docs](https://docs.arize.com/phoenix) for the latest image and ports. A typical local run (verify tag on Docker Hub / docs before use):

```bash
docker run --rm -p 6006:6006 arizephoenix/phoenix:latest
```

Open the UI URL shown in container logs (often `http://localhost:6006`).

Then either:

1. Point a small Python script using the Phoenix SDK at this instance, or  
2. Point **OTLP** from a test app if your Phoenix version exposes OTLP on a documented port.

## Option B — OpenInference in cluster

Check the [OpenInference](https://github.com/Arize-ai/openinference) repositories for Helm/Kubernetes instructions. Success criterion for prep: **one span or experiment record** visible in UI.

## If blocked

Document the blocker (version, missing ARM image, auth) in your notes and move on — the course will deep-dive.
