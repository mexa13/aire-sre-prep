# Local MCP server (prep)

**When:** [START-HERE.md](START-HERE.md) **Phase J** (after cluster prep; MCP does not need the cluster).

---

## What connects to what (read this first)

This repo’s **`mcp-server`** is only an **MCP *tool server***: it exposes tools like `echo` and `add` over **stdio** to a **host** (e.g. Cursor).

It does **not** embed an LLM and does **not** call Qwen by itself.

```text
┌─────────────────────────────────────────────────────────────┐
│  Your IDE (e.g. Cursor)                                      │
│  ┌─────────────────────┐    ┌─────────────────────────────┐ │
│  │ Chat / agent “brain” │    │ MCP client (tools)         │ │
│  │ → calls LLM API      │    │ → spawns stdio process     │ │
│  └──────────┬──────────┘    └──────────────┬──────────────┘ │
└─────────────┼──────────────────────────────┼───────────────┘
              │                              │
              ▼                              ▼
   OpenAI-compatible HTTP API          python main.py
   (LM Studio local server,            (this repo’s mcp-server)
    OpenAI cloud, etc.)
```

| Piece | Role |
|--------|------|
| **LLM API** (LM Studio, etc.) | Model answers: planning, text, code. Configured in the **IDE** as the chat model provider. |
| **MCP server** (`mcp-server/`) | **Tools** the agent can invoke (stdio). Independent of which model backs the agent. |

So: **Qwen in LM Studio** = where the **model** runs for Cursor’s agent. **`mcp-server`** = extra **actions** the agent can call. They are **two different integrations** in Cursor settings.

---

## LM Studio + Cursor + this MCP server (e.g. Qwen 35B MoE)

1. **LM Studio**  
   - Load your model (e.g. Qwen variant you named).  
   - Start the **Local Server** (OpenAI-compatible API).  
   - Note the base URL (often `http://127.0.0.1:1234/v1` — check LM Studio UI).

2. **Cursor — model / LLM**  
   - Point the editor’s **OpenAI-compatible** provider at that base URL (and set an API key if the UI requires one; LM Studio often accepts any placeholder).  
   - Exact menu names change between Cursor versions; look for custom OpenAI base URL / model override.

3. **Cursor — MCP**  
   - Add an MCP server entry that runs **this repo’s** `main.py` with the venv Python (see JSON below).  
   - That is **only** for tools `echo` / `add`, not for selecting Qwen.

4. **Check**  
   - Chat uses Qwen via LM Studio.  
   - Agent can still call MCP tools (if the agent workflow uses tools).

If something breaks, test **LM Studio** alone with `curl` to `/v1/models` or a small chat completion; test **MCP** alone with `./verify.sh` and tool calls in the client.

---

## Quick verify (non-interactive)

```bash
cd mcp-server
chmod +x verify.sh
./verify.sh
```

## Two ways to run the server (pick one)

**A — Cursor runs it (normal)**  
You only add the MCP entry under **Cursor Settings → MCP** (JSON below). Cursor **starts** `python main.py` when the session needs tools and talks to it over stdio. **Do not** also run `python main.py` in a terminal for daily use.

**B — Terminal (debug only)**  
`python main.py` blocks the terminal and waits for stdio. That matches **manual** clients (some CLIs, tests). Cursor does not use that terminal process unless you wired something unusual.

---

## After you wired Cursor: what to do next

### 1. Confirm the server is actually connected

1. Open **Cursor Settings** → search **MCP** (or **Features → MCP**, depending on version).
2. Find your server name (e.g. `aire-prep-lab`). It should show as **connected** / **enabled**, not error.
3. If there is a **Tools** or **Resources** list for that server, you should see tools named **`echo`** and **`add`** (from [main.py](../mcp-server/main.py)).

If you see a spawn error, fix **absolute paths** in JSON and ensure `.venv` exists and `pip install -r requirements.txt` was run once.

### 2. Where requests come from

| Source | What happens |
|--------|----------------|
| **You** | You type a message in **Chat** or **Agent / Composer** (the mode that can use tools). |
| **Cursor** | Sends JSON-RPC over stdio to `main.py`: list tools, then `tools/call` for `echo` or `add`. |
| **This repo** | Only implements those two tools; there is **no HTTP** and **no** outgoing “requests” to the internet from `main.py`. |

You do **not** open a browser or `curl` the MCP server. The only “traffic” is **your IDE ↔ local Python process**.

### 3. How to verify with a real tool call

Use **Agent** (or the mode your Cursor version labels as able to use **MCP tools** — not every plain chat uses tools).

Try prompts like (copy one):

- `Call the MCP tool echo with text: hello-aire-prep`
- `Using my MCP server, use add with a=21 and b=21 and tell me the integer result`
- `List available MCP tools from aire-prep-lab and invoke echo with text "ok"`

**Success:** the reply includes **`hello-aire-prep`**, **`42`**, or **`ok`**, and the UI often shows a **tool call** step (tool name + arguments + result).

**Failure:** the model answers without calling tools, or says it has no tools — switch to **Agent**, check MCP green in settings, or try a more explicit prompt (“You must call the tool, do not guess”).

### 4. What each tool expects (exact parameters)

| Tool | Parameters | Example result |
|------|------------|----------------|
| `echo` | `text` (string) | Returns the same string |
| `add` | `a`, `b` (integers) | Returns `a + b` |

### 5. Optional: see that something is happening

- **Output / MCP logs:** some Cursor builds show MCP or subprocess logs in **Output** panel → pick **MCP** (or similar) from the dropdown.
- **Terminal:** only if you chose **way B** above; with **way A**, the process is child of Cursor, not your shell.

---

## Run stdio server manually (debug / non-Cursor clients)

```bash
cd mcp-server
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

## Cursor — MCP config only (tools)

Use **absolute paths** on your machine:

```json
{
  "mcpServers": {
    "aire-prep-lab": {
      "command": "/absolute/path/to/aire-sre-prep/mcp-server/.venv/bin/python",
      "args": ["/absolute/path/to/aire-sre-prep/mcp-server/main.py"],
      "cwd": "/absolute/path/to/aire-sre-prep/mcp-server"
    }
  }
}
```

## Prep goals

- **`echo` / `add`** succeed from the client.  
- You can explain: **LLM endpoint** (LM Studio) vs **MCP tools** (this server).  
- On the course, gateway/auth will attach to **remote** MCP and models — same separation of concerns.
