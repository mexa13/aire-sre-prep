"""
ADK lab agent: kubectl-backed tools for cluster inspection.

Copy this file into your ADK app folder after `adk create prep_adk_smoke`, overwriting
the generated `agent.py`:

  cp examples/prep_adk_smoke/agent.py /tmp/prep_adk_smoke/agent.py

Requires `kubectl` on PATH and a valid kubeconfig (e.g. kind-aire-prep context).
"""
from __future__ import annotations

import subprocess

from google.adk.agents.llm_agent import Agent


def _run_kubectl(args: list[str], timeout_seconds: int = 30) -> str:
    """Run kubectl safely and return stdout/stderr text."""
    cmd = ["kubectl", *args]
    try:
        completed = subprocess.run(
            cmd,
            check=False,
            capture_output=True,
            text=True,
            timeout=timeout_seconds,
        )
    except subprocess.TimeoutExpired:
        return f"Command timed out after {timeout_seconds}s: {' '.join(cmd)}"
    except OSError as exc:
        return f"Failed to run command {' '.join(cmd)}: {exc}"

    output = (completed.stdout or "").strip()
    err = (completed.stderr or "").strip()
    if completed.returncode == 0:
        return output or "(no output)"
    return (
        f"kubectl exited with {completed.returncode}\nSTDOUT:\n{output}\nSTDERR:\n{err}"
    )


def k8s_current_context() -> str:
    """Return current kubectl context and default namespace from kubeconfig."""
    context = _run_kubectl(["config", "current-context"])
    ns = _run_kubectl(
        ["config", "view", "--minify", "--output", "jsonpath={..namespace}"]
    )
    if not ns or "kubectl exited" in ns:
        ns = "default"
    return f"Current context: {context}\nDefault namespace: {ns}"


def k8s_nodes() -> str:
    """List cluster nodes with status and versions."""
    return _run_kubectl(["get", "nodes", "-o", "wide"])


def k8s_workloads(namespace: str = "default") -> str:
    """List pods, deployments, and services in a namespace."""
    return _run_kubectl(["get", "pods,deploy,svc", "-n", namespace, "-o", "wide"])


def k8s_recent_events(namespace: str = "default") -> str:
    """Show recent Kubernetes events in a namespace."""
    return _run_kubectl(
        ["get", "events", "-n", namespace, "--sort-by=.metadata.creationTimestamp"]
    )


def k8s_describe_pod(namespace: str, pod_name: str) -> str:
    """Describe a specific pod for troubleshooting."""
    return _run_kubectl(["describe", "pod", pod_name, "-n", namespace])


def k8s_logs(namespace: str, pod_name: str, container: str = "") -> str:
    """Get recent pod logs (last 200 lines). Optionally set container for multi-container pods."""
    args = ["logs", pod_name, "-n", namespace, "--tail=200"]
    if container:
        args.extend(["-c", container])
    return _run_kubectl(args)


def k8s_top_nodes() -> str:
    """Show node CPU/memory usage (requires metrics-server)."""
    return _run_kubectl(["top", "nodes"])


def k8s_ingress_svc_endpoints(namespace: str) -> str:
    """List Ingress, Services, and Endpoints in a namespace (debug hostnames / routing)."""
    blocks: list[str] = []
    for kind in ("ingress", "svc", "endpoints"):
        blocks.append(f"=== {kind.upper()} ===")
        blocks.append(_run_kubectl(["get", kind, "-n", namespace, "-o", "wide"]))
        blocks.append("")
    return "\n".join(blocks).strip()


root_agent = Agent(
    model="gemini-2.5-flash",
    name="root_agent",
    description="Kubernetes troubleshooting assistant using kubectl tools.",
    instruction=(
        "You help inspect and troubleshoot Kubernetes clusters. "
        "Always prefer tools over guessing. "
        "When the user asks about cluster state, check context first, then relevant "
        "namespaces (e.g. aire-prep, kagent, ingress-nginx). "
        "Use k8s_top_nodes when they ask about capacity or pressure; use "
        "k8s_ingress_svc_endpoints when URLs or ingress do not work. "
        "If metrics-server is missing, kubectl top will fail — explain that and suggest "
        "kubectl get apiservice | grep metrics."
    ),
    tools=[
        k8s_current_context,
        k8s_nodes,
        k8s_workloads,
        k8s_recent_events,
        k8s_describe_pod,
        k8s_logs,
        k8s_top_nodes,
        k8s_ingress_svc_endpoints,
    ],
)
