# SLO lab: TTFT-style framing (prep)

Classic SLOs focus on availability and latency. Generative stacks often add **time-to-first-token (TTFT)** and **time-per-output-token (TPOT)**. In this lab you approximate them against **fake-llm** (stub delays).

## SLI candidates

| SLI | How you measure it (prep) |
|-----|----------------------------|
| Success rate | Non-5xx responses / total (`hey` or `k6` summary) |
| Latency p95 | Total request time for `POST /v1/chat/completions` |
| TTFT proxy | Time to first byte (streaming) or `lab_meta.handler_latency_ms` (JSON) from stub |

## Experiments

```bash
# Simple latency (non-streaming)
curl -s -o /dev/null -w "total_time=%{time_total}s\n" \
  -H "Content-Type: application/json" \
  -d '{"model":"fake","messages":[{"role":"user","content":"hi"}]}' \
  http://fake-llm.aire-prep.local/v1/chat/completions
```

```bash
# Optional: hey load test
hey -n 500 -c 20 -m POST -T "application/json" \
  -d '{"model":"fake","messages":[{"role":"user","content":"x"}]}' \
  http://fake-llm.aire-prep.local/v1/chat/completions
```

Record **p95 / error %** and a one-line **draft SLO** (e.g. “95% of stub requests complete under 500 ms”).

## Error budget (idea)

For learning only: if you allow **30 minutes** of “bad” latency per week in the lab, what fraction of failed `hey` runs would exhaust it? Relate to how you’d define budget on a real gateway in production.
