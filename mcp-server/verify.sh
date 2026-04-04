#!/usr/bin/env bash
# Smoke-test: venv, deps, and main.py load (stdio server is interactive; see docs/MCP.md).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT"
if [[ ! -d .venv ]]; then
  python3 -m venv .venv
fi
./.venv/bin/pip install -q -r requirements.txt
./.venv/bin/python -c "import importlib.util; s=importlib.util.spec_from_file_location('m','main.py'); m=importlib.util.module_from_spec(s); s.loader.exec_module(m); assert hasattr(m,'mcp'); print('ok: FastMCP app loaded')"
echo "Next: run ./.venv/bin/python main.py (stdio) or attach from your MCP client per ../docs/MCP.md"
