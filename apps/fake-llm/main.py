"""Stub OpenAI-compatible HTTP API for lab ingress, SLO, and tracing practice."""

from __future__ import annotations

import asyncio
import json
import os
import time
import uuid
from typing import Any

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, StreamingResponse
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

app = FastAPI(title="fake-llm", version="0.1.0")

_otel_endpoint = os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT", "")
if _otel_endpoint:
    _grpc_ep = (
        _otel_endpoint.replace("http://", "")
        .replace("https://", "")
        .replace("grpc://", "")
    )
    resource = Resource.create(
        {
            "service.name": os.getenv("OTEL_SERVICE_NAME", "fake-llm"),
            "service.namespace": os.getenv("POD_NAMESPACE", "aire-prep"),
        }
    )
    provider = TracerProvider(resource=resource)
    exporter = OTLPSpanExporter(endpoint=_grpc_ep, insecure=True)
    provider.add_span_processor(BatchSpanProcessor(exporter))
    trace.set_tracer_provider(provider)
    FastAPIInstrumentor.instrument_app(app)


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/metrics")
async def metrics_placeholder() -> str:
    """Reserved for Prometheus-style metrics in later exercises."""
    return ""


@app.post("/v1/chat/completions")
async def chat_completions(request: Request) -> Any:
    tracer = trace.get_tracer(__name__)
    body: dict[str, Any] = {}
    try:
        body = await request.json()
    except json.JSONDecodeError:
        pass

    stream = bool(body.get("stream", False))
    # Simulate TTFT: small configurable delay (milliseconds)
    ttft_ms = int(os.getenv("FAKE_LLM_TTFT_MS", "25"))
    t0 = time.perf_counter()

    if stream:

        async def gen():
            with tracer.start_as_current_span("fake_stream"):
                await _sleep_ms_async(ttft_ms)
                chunk = {
                    "id": f"chatcmpl-{uuid.uuid4().hex[:8]}",
                    "object": "chat.completion.chunk",
                    "choices": [
                        {
                            "index": 0,
                            "delta": {"content": "fake "},
                            "finish_reason": None,
                        }
                    ],
                }
                yield f"data: {json.dumps(chunk)}\n\n"
                await _sleep_ms_async(int(os.getenv("FAKE_LLM_TOKEN_MS", "5")))
                chunk["choices"][0]["delta"] = {"content": "token stream"}

                yield f"data: {json.dumps(chunk)}\n\n"
                yield "data: [DONE]\n\n"

        return StreamingResponse(gen(), media_type="text/event-stream")

    with tracer.start_as_current_span("fake_completion"):
        await _sleep_ms_async(ttft_ms)
        latency_ms = (time.perf_counter() - t0) * 1000
        return JSONResponse(
            {
                "id": f"chatcmpl-{uuid.uuid4().hex[:8]}",
                "object": "chat.completion",
                "model": body.get("model", "fake"),
                "choices": [
                    {
                        "index": 0,
                        "message": {"role": "assistant", "content": "fake-llm stub response"},
                        "finish_reason": "stop",
                    }
                ],
                "usage": {"prompt_tokens": 1, "completion_tokens": 4, "total_tokens": 5},
                "lab_meta": {
                    "ttft_simulated_ms": ttft_ms,
                    "handler_latency_ms": round(latency_ms, 3),
                },
            }
        )


async def _sleep_ms_async(ms: int) -> None:
    if ms > 0:
        await asyncio.sleep(ms / 1000.0)
