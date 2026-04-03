# Local MCP server (prep)

The [mcp-server/](../mcp-server) directory contains a tiny **stdio** MCP server built with `FastMCP`.

## Run

```bash
cd mcp-server
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

The process waits on stdio for the host (Cursor, Claude Desktop, or another MCP client).

## Cursor

Add a **User** or **Project** MCP config that runs this server (exact JSON depends on your Cursor version). Typical shape:

```json
{
  "mcpServers": {
    "aire-prep-lab": {
      "command": "python",
      "args": ["/absolute/path/to/aire-sre-prep/mcp-server/main.py"],
      "cwd": "/absolute/path/to/aire-sre-prep/mcp-server"
    }
  }
}
```

Prefer calling the venv interpreter so dependencies resolve:

```json
"command": "/absolute/path/to/aire-sre-prep/mcp-server/.venv/bin/python",
"args": ["/absolute/path/to/aire-sre-prep/mcp-server/main.py"]
```

## Prep goals

- Confirm **tool listing** and **`add` / `echo`** calls work.
- Enable logging in your client and relate MCP round-trips to **gateway / auth** topics from the course (rate limits, credentials) once you move beyond stdio.
