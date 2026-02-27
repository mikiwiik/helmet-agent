# helmet-agent

A conversational AI agent that answers questions about the Helsinki metropolitan area **Helmet** public library network — search for books, check which branches hold them, and look up opening hours.

**Example:**
> "Which books by Väinö Linna are available in Munkkiniemi?"

## How it works

1. User asks a question in natural language (Finnish or English)
2. Claude decomposes it into tool calls against two public APIs:
   - **Finna API** (`api.finna.fi`) — material search, branch locations
   - **Kirkanta API** (`api.kirjastot.fi`) — opening hours, library info
3. Results are synthesized into a human-readable answer with links

## Project documentation

| File | Contents |
|------|----------|
| [CLAUDE.md](CLAUDE.md) | Development practices (atomic commits, conventional commits, TDD) |
| [todo.md](todo.md) | Implementation checklist |
| [docs/requirements.md](docs/requirements.md) | Functional and non-functional requirements |
| [docs/use_cases.md](docs/use_cases.md) | User-facing scenarios and test cases |
| [docs/adr/](docs/adr/) | Architecture Decision Records |

### ADRs

- [001 — Python runtime](docs/adr/001-python-runtime.md)
- [002 — Finna API as primary data source](docs/adr/002-finna-api-as-primary-data-source.md)
- [003 — Kirkanta API for opening hours](docs/adr/003-kirkanta-api-for-opening-hours.md)
- [004 — Claude tool-use for agent orchestration](docs/adr/004-claude-tool-use-for-agent.md)

## Tech stack

- Python 3.12+
- `httpx` — async HTTP client
- `anthropic` — Claude API SDK
- `pytest` — test runner
- `ruff` — linter/formatter

## Known limitations

- Finna API shows which branches **hold** an item but not real-time loan status (on shelf vs. checked out)
- Opening hours come from a separate API (Kirkanta), requiring name mapping between the two systems
