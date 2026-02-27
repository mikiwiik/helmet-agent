# CLAUDE.md — Project Practices

## Commit discipline
- **Atomic commits** — each commit does one thing
- **Conventional commits** — `feat:`, `fix:`, `docs:`, `test:`, `refactor:`, `chore:`
- Examples: `feat: add branch name fuzzy resolver`, `test: search tool returns paginated results`

## Development approach
- **TDD** — write a failing test first, then implement, then refactor
- Tests live in `tests/` mirroring `src/` structure
- Use `pytest` as the test runner

## Code style
- Python 3.12+
- Type hints on all public functions
- `ruff` for linting and formatting
- Keep functions short and focused

## Architecture
This is an **MCP server** — not a standalone agent. Claude Code/Desktop is the host.
- We implement tools, not orchestration
- Each tool is a `@mcp.tool()` decorated async function
- Tools return strings; Claude handles reasoning and presentation

## Project structure
```
src/helmet_agent/
  server.py             # FastMCP server entry point
  tools.py              # @mcp.tool() definitions (search, record, branches, hours)
  finna.py              # Finna REST API client
  kirkanta.py           # Kirkanta API client (opening hours)
  branch_resolver.py    # fuzzy branch name → building code (static mapping)
tests/
  test_finna.py
  test_kirkanta.py
  test_branch_resolver.py
  test_tools.py         # unit tests for MCP tools (mocked HTTP)
  test_integration.py   # end-to-end tests against real APIs (@pytest.mark.integration)
```

## Key files
- `docs/adr/` — Architecture Decision Records
- `docs/requirements.md` — Functional and non-functional requirements
- `docs/use_cases.md` — Expressed and tested use cases
- `todo.md` — Implementation checklist
