# Helmet Library Agent - Implementation Plan

An MCP server that exposes Helmet library tools to Claude Code / Claude Desktop. Users ask natural-language questions; Claude calls the tools and synthesizes answers.

**Example prompt:** "Which books by Väinö Linna are available in Munkkiniemi?"

---

## Finna API Reference

- **Base URL:** `https://api.finna.fi/v1/`
- **OpenAPI spec:** `https://api.finna.fi/api/v1/?openapi`
- **Auth:** None required (public, CORS enabled)
- **Rate limits:** Not documented; API not designed for bulk downloads

### Key Endpoints

| Endpoint | Purpose |
|----------|---------|
| `GET /v1/search` | Search materials by keyword, author, title, format, building |
| `GET /v1/record` | Fetch detailed record info (holdings, availability) |

### Search Parameters

| Param | Example | Notes |
|-------|---------|-------|
| `lookfor` | `väinö linna` | Free-text search query |
| `type` | `Author`, `Title`, `AllFields` | Search field |
| `filter[]` | `building:"0/Helmet/"` | Restrict to Helmet libraries |
| `filter[]` | `building:"2/Helmet/h/h55/"` | Restrict to specific branch |
| `filter[]` | `format:"0/Book/"` | Books only |
| `field[]` | `title`, `id`, `buildings`, `year`, `authors`, `formats` | Fields to return |
| `limit` | `20` (max 100) | Results per page |
| `page` | `1`-`5000` | Pagination |
| `facet[]` | `building`, `format` | Get available filter values |
| `lng` | `fi`, `en-gb`, `sv` | Language for translated values |

### Building Code Hierarchy (Helmet)

Buildings use a hierarchical slash notation:
- `0/Helmet/` — All Helmet libraries
- `1/Helmet/h/` — Helsinki, `1/Helmet/e/` — Espoo, `1/Helmet/v/` — Vantaa, `1/Helmet/k/` — Kauniainen
- `2/Helmet/h/h01/` — Pasila, `2/Helmet/h/h82/` — Roihuvuori, etc.

Branch codes (level 2) need to be discovered via facet queries or maintained as a lookup table.

### Record Fields

Records return: `id`, `title`, `authors`, `formats`, `buildings` (which branches hold it), `year`, `languages`, `subjects`, `images`, `series`, `rating`

### What the API does NOT provide directly

- **Real-time item-level availability** (on shelf / checked out) — the `buildings` field shows which branches have the item in their collection, but not current loan status
- **Opening hours** — not available via the search/record API; use Kirkanta API instead

## Kirkanta API Reference

- **Base URL:** `https://api.kirjastot.fi/v4/`
- **Auth:** None required
- **Key endpoint:** `GET /v4/library?city.name=helsinki&with=schedules`
- Returns: name, address, coordinates, opening hours, contact info
- 92 Helsinki municipal libraries indexed

---

## Implementation Steps

### 1. Set up project skeleton
- [ ] Init with `uv init` + `pyproject.toml` (Python 3.12+)
- [ ] Dependencies: `mcp[cli]`, `httpx`, `pytest`, `ruff`
- [ ] Create `src/helmet_agent/` and `tests/` directories

### 2. Build Finna API client (`src/helmet_agent/finna.py`)
- [ ] Implement `search(query, type, filters, fields, limit)` → calls `/v1/search`
- [ ] Implement `get_record(id, fields)` → calls `/v1/record`
- [ ] Implement `get_building_facets()` → discover branch codes
- [ ] Handle pagination for large result sets
- [ ] Tests with mocked HTTP responses

### 3. Build branch name resolver (`src/helmet_agent/branch_resolver.py`)
- [ ] Fetch all Helmet building facets and cache locally
- [ ] Fuzzy match: "Munkkiniemi" → `2/Helmet/h/h55/`
- [ ] Handle ambiguity (return multiple matches)
- [ ] Tests for exact, fuzzy, and ambiguous matches

### 4. Build Kirkanta client (`src/helmet_agent/kirkanta.py`)
- [ ] Implement `search_libraries(city, name)` → calls `/v4/library`
- [ ] Implement `get_schedules(library_id)` → calls `/v4/library/{id}?with=schedules`
- [ ] Tests with mocked HTTP responses

### 5. Build MCP server (`src/helmet_agent/server.py`)
- [ ] `FastMCP("helmet")` entry point
- [ ] Tool: `search_materials(query, author, title, format, branch)` — search + branch resolve + format results
- [ ] Tool: `get_record_detail(record_id)` — full record info
- [ ] Tool: `list_library_branches(city)` — list available branches
- [ ] Tool: `get_opening_hours(library_name)` — Kirkanta lookup
- [ ] Integration tests calling tools end-to-end

### 6. Configuration & usage
- [ ] Document Claude Code config: `claude mcp add helmet-library`
- [ ] Add `__main__.py` entry point for `uv run`
- [ ] Test full flow in Claude Code

---

## Resolved Decisions

- **Python** chosen as runtime (see [ADR-001](docs/adr/001-python-runtime.md))
- **MCP server** as delivery mechanism (see [ADR-005](docs/adr/005-mcp-server-as-delivery.md))
- **Kirkanta API** confirmed working for opening hours (see [ADR-003](docs/adr/003-kirkanta-api-for-opening-hours.md))

## Open Questions

- **Real-time availability:** Finna shows which branches *own* an item but not loan status. Accept as known limitation for now.
- **Branch name mapping:** Need to map between Finna building codes and Kirkanta library IDs. Both use Finnish names — fuzzy match should work.
