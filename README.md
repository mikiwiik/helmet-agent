# helmet-agent

An MCP server that gives Claude access to the Helsinki **Helmet** public library network — search for books, check which branches hold them, and look up opening hours.

## Usage

Once configured, just ask Claude naturally:

> "Which books by Väinö Linna are available in Munkkiniemi?"
> "When is Kallio library open tomorrow?"
> "Find audiobooks of Sinuhe egyptiläinen"

## How it works

This is an **MCP (Model Context Protocol) server** that exposes library tools to Claude Code or Claude Desktop. Claude handles the reasoning — the server provides the data.

**Tools exposed:**
| Tool | Description |
|------|-------------|
| `search_materials` | Search books, audiobooks, DVDs etc. by author, title, or keyword. Filter by branch. |
| `get_record_detail` | Get full details for a specific library record |
| `list_library_branches` | List Helmet library branches by city |
| `get_opening_hours` | Look up opening hours for a library |

**Data sources:**
- [Finna API](https://api.finna.fi/) — material search and branch locations
- [Kirkanta API](https://api.kirjastot.fi/v4/) — opening hours and library info

## Setup

```bash
# Install
uv pip install -e .

# Add to Claude Code
claude mcp add helmet-library -- uv run helmet-agent
```

## Project documentation

| File | Contents |
|------|----------|
| [CLAUDE.md](CLAUDE.md) | Development practices (atomic commits, conventional commits, TDD) |
| [todo.md](todo.md) | Implementation checklist with API reference |
| [docs/requirements.md](docs/requirements.md) | Functional and non-functional requirements |
| [docs/use_cases.md](docs/use_cases.md) | User-facing scenarios and test cases |
| [docs/adr/](docs/adr/) | Architecture Decision Records |

### ADRs

- [001 — Python runtime](docs/adr/001-python-runtime.md)
- [002 — Finna API as primary data source](docs/adr/002-finna-api-as-primary-data-source.md)
- [003 — Kirkanta API for opening hours](docs/adr/003-kirkanta-api-for-opening-hours.md)
- [004 — Claude tool-use for agent](docs/adr/004-claude-tool-use-for-agent.md) *(superseded by 005)*
- [005 — MCP server as delivery mechanism](docs/adr/005-mcp-server-as-delivery.md)

## Known limitations

- Finna API shows which branches **hold** an item but not real-time loan status (on shelf vs. checked out)
- Opening hours come from a separate API (Kirkanta), requiring name mapping between the two systems
