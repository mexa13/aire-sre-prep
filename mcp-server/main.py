#!/usr/bin/env python3
"""Minimal MCP server for local prep (stdio + HTTP transports)."""

import os
from mcp.server.fastmcp import FastMCP

MCP_TRANSPORT = os.getenv("MCP_TRANSPORT", "stdio").strip().lower()
MCP_HOST = os.getenv("MCP_HOST", "127.0.0.1")
MCP_PORT = int(os.getenv("MCP_PORT", "8000"))
MCP_MOUNT_PATH = os.getenv("MCP_MOUNT_PATH", "/")
MCP_STREAMABLE_HTTP_PATH = os.getenv("MCP_STREAMABLE_HTTP_PATH", "/mcp")

mcp = FastMCP(
    "aire-prep-lab",
    host=MCP_HOST,
    port=MCP_PORT,
    mount_path=MCP_MOUNT_PATH,
    streamable_http_path=MCP_STREAMABLE_HTTP_PATH,
)


@mcp.tool()
def echo(text: str) -> str:
    """Return the same text; use to verify MCP wiring."""
    return text


@mcp.tool()
def add(a: int, b: int) -> int:
    """Add two integers (smoke test)."""
    return a + b


if __name__ == "__main__":
    if MCP_TRANSPORT == "streamable-http":
        mcp.run(transport="streamable-http")
    elif MCP_TRANSPORT == "sse":
        mcp.run(transport="sse")
    else:
        mcp.run(transport="stdio")
