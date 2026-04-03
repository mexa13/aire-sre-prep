# Course stack smoke tests (install only)

Tools from the course announcement evolve. Prep goal: **read README → install → one scenario** (routing, rate limit, or hello agent). Pin versions in [VERSION-PINS.md](VERSION-PINS.md).

Search and open the **current** upstream repo / docs for each name below; replace URLs if projects move.

| Tool / area | Prep goal |
|-------------|-----------|
| **Agent Gateway** | Helm/kubectl install; single route to a stub backend; note auth header pattern. |
| **Kagent** | Agent runs in cluster; one tool call succeeds; note CRDs installed. |
| **llm-d** | One workload scheduled; note GPU vs CPU assumptions. |
| **kmcp** | One MCP server registered per quickstart. |
| **ADK / A2A** | Concept + official hello-world only if time permits. |

## Template (copy per tool)

```text
Tool:
Version / chart / image:
Install command(s):
Single test command:
Failure / follow-up:
```

## Notes

- Prefer **kind load** or an **in-cluster registry** for images you build.
- If two tools both want ingress: use separate hostnames or paths and document conflicts.
