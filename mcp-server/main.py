#!/usr/bin/env python3
"""Minimal MCP server for local prep (stdio transport)."""

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("aire-prep-lab")


@mcp.tool()
def echo(text: str) -> str:
    """Return the same text; use to verify MCP wiring."""
    return text


@mcp.tool()
def add(a: int, b: int) -> int:
    """Add two integers (smoke test)."""
    return a + b


if __name__ == "__main__":
    mcp.run()
