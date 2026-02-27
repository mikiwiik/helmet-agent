# CLAUDE.md — Project Practices

## Commit discipline
- **Atomic commits** — each commit does one thing
- **Conventional commits** — `feat:`, `fix:`, `docs:`, `test:`, `refactor:`, `chore:`
- Examples: `feat: add branch name fuzzy resolver`, `test: search client returns paginated results`

## Development approach
- **TDD** — write a failing test first, then implement, then refactor
- Tests live alongside source in `tests/` mirroring `src/` structure
- Use `pytest` as the test runner

## Code style
- Python 3.12+
- Type hints on all public functions
- `ruff` for linting and formatting
- Keep functions short and focused

## Project structure
```
src/helmet_agent/       # main package
  finna_client.py       # Finna REST API wrapper
  kirkanta_client.py    # Kirkanta API wrapper (opening hours)
  branch_resolver.py    # fuzzy branch name → building code
  agent.py              # Claude tool-use orchestration
  tools.py              # tool definitions for the agent
tests/
  test_finna_client.py
  test_kirkanta_client.py
  test_branch_resolver.py
  test_agent.py
```

## Key files
- `docs/adr/` — Architecture Decision Records
- `docs/requirements.md` — Functional and non-functional requirements
- `docs/use_cases.md` — Expressed and tested use cases
- `todo.md` — Implementation checklist
