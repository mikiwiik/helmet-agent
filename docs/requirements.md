# Requirements

## Functional

### FR-1: Material search
The agent must search for library materials (books, audiobooks, DVDs, etc.) by author, title, or free-text query within the Helmet library network.

### FR-2: Branch filtering
The agent must filter results by library branch using natural-language names (e.g. "Munkkiniemi", "Oodi", "Kallio") resolved to Finna building codes.

### FR-3: Availability information
The agent must show which branches hold a given item. Note: real-time loan status (on shelf vs. checked out) is a known limitation of the Finna API.

### FR-4: Opening hours
The agent must answer questions about library opening hours using the Kirkanta API.

### FR-5: Natural language interface
Users interact with the agent via plain Finnish or English prompts. The agent decomposes questions into API calls and synthesizes a human-readable answer.

### FR-6: Record links
Responses must include direct links to the Helmet Finna record page (`https://helmet.finna.fi/Record/{id}`).

## Non-functional

### NFR-1: No authentication required
Both Finna and Kirkanta APIs are public. The agent must not require library credentials from users.

### NFR-2: Graceful degradation
If an API is unreachable or returns errors, the agent must inform the user clearly rather than crash.

### NFR-3: Response latency
Agent responses should complete within a reasonable time (~5-10s) for typical queries.

### NFR-4: Offline-safe branch resolution
Branch name-to-code mapping should be cached locally so it doesn't require a network call on every query.

---

## Setup Guide

### Prerequisites

1. **Python 3.12+** — check with `python3 --version`
2. **uv** — fast Python package manager
   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```
3. **Claude Code** or **Claude Desktop**
   - Claude Code: `npm install -g @anthropic-ai/claude-code`
   - Claude Desktop: download from [claude.ai/download](https://claude.ai/download)
   - Both require a Claude Pro/Max subscription or Anthropic API key.

### Install the MCP server

```bash
git clone https://github.com/mikiwiik/helmet-agent.git
cd helmet-agent
uv sync
```

### Option A: Register with Claude Code

```bash
claude mcp add helmet-library -- uv run --directory /absolute/path/to/helmet-agent helmet-agent
```

Verify it's registered:

```bash
claude mcp list
```

Start Claude Code and ask questions naturally. Use `/mcp` inside a session to check server status or restart the server.

### Option B: Register with Claude Desktop

Open your Claude Desktop config file:

- **macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows:** `%APPDATA%\Claude\claude_desktop_config.json`

You can also reach this via Claude Desktop: **Settings > Developer > Edit Config**.

Add the helmet-library server (create the file if it doesn't exist):

```json
{
  "mcpServers": {
    "helmet-library": {
      "command": "uv",
      "args": ["run", "--directory", "/absolute/path/to/helmet-agent", "helmet-agent"]
    }
  }
}
```

Replace `/absolute/path/to/helmet-agent` with the actual path where you cloned the repo.

Restart Claude Desktop. A hammer icon appears in the input box — click it to verify the helmet-library tools are loaded.

### Usage

Ask questions in natural language:

- "Which books by Väinö Linna are available in Munkkiniemi?"
- "When is Kallio library open tomorrow?"
- "Find audiobooks of Sinuhe egyptiläinen in Espoo"
- "What libraries are there in Vantaa?"

Claude will automatically call the helmet-library tools when your question is about the Helmet library network.

### Troubleshooting

- **"Tool not found"** — Claude Code: run `claude mcp list`. Claude Desktop: check the hammer icon for registered tools.
- **Server not starting** — verify `uv` is in your PATH (`which uv`). If not, use the full path to `uv` in the config (e.g. `/Users/you/.local/bin/uv`).
- **Slow first response** — the first API call may take a moment to establish a connection
- **No results** — try broadening the search (remove branch filter, use different spelling)
