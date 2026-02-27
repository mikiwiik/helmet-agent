# Helmet Library Agent - Implementation Plan

An AI agent that answers natural-language questions about Helsinki's Helmet library system (books, availability, locations, hours) by querying the public Finna REST API.

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
- **Opening hours** — not available via the search/record API; would need scraping from `helmet.finna.fi/OrganisationInfo/Home` or a separate data source (Kirkanta API: `api.kirjastot.fi`)

---

## Implementation Steps

### 1. Set up project skeleton
- [ ] Init Python project with `pyproject.toml` (Python 3.12+)
- [ ] Dependencies: `httpx`, `anthropic`, `pytest`, `ruff`
- [ ] Create `src/helmet_agent/` and `tests/` directories

### 2. Build Finna API client
- [ ] Implement `search(query, type, filters, fields, limit)` wrapper around `/v1/search`
- [ ] Implement `get_record(id, fields)` wrapper around `/v1/record`
- [ ] Implement `get_building_facets(parent_building)` to discover branch codes
- [ ] Build a **branch name-to-code resolver** (fuzzy match "Munkkiniemi" → `2/Helmet/h/h55/`)
- [ ] Handle pagination for large result sets

### 3. Integrate Kirkanta API for opening hours
- [ ] `api.kirjastot.fi` provides library info, opening hours, contact details
- [ ] Implement `get_library_info(name)` and `get_opening_hours(library_id)`
- [ ] Map between Finna building codes and Kirkanta library IDs

### 4. Build the agent layer
- [ ] Define tools the LLM can call:
  - `search_materials(query, author, title, format, library_branch)`
  - `get_record_detail(record_id)`
  - `list_library_branches(city)`
  - `get_opening_hours(library_name)`
- [ ] Write system prompt that instructs the LLM how to decompose user questions into tool calls
- [ ] Use Claude API with tool_use (or Anthropic Agent SDK) to orchestrate

### 5. Branch name resolution
- [ ] On first run / periodically: fetch all Helmet building facets and cache them
- [ ] Build fuzzy matcher: user says "Munkkiniemi" → find closest match in cached branch names
- [ ] Handle ambiguity (ask user to clarify if multiple matches)

### 6. Response formatting
- [ ] Parse API results into human-readable answers
- [ ] Include: title, author, year, format, which branches hold it
- [ ] Link to the Finna record page: `https://helmet.finna.fi/Record/{id}`

### 7. Testing & polish
- [ ] Test with representative queries (author search, title search, branch filtering)
- [ ] Handle edge cases: no results, ambiguous branch names, API errors
- [ ] Add basic CLI interface for interactive use

---

## Resolved Decisions

- **Python** chosen as runtime (see [ADR-001](docs/adr/001-python-runtime.md))
- **Kirkanta API** confirmed working for opening hours — 92 Helsinki libraries indexed, supports `?with=schedules` (see [ADR-003](docs/adr/003-kirkanta-api-for-opening-hours.md))

## Open Questions

- **Real-time availability:** Finna shows which branches *own* an item but not loan status. Accept as known limitation for now.
- **Branch name mapping:** Need to map between Finna building codes and Kirkanta library IDs. Both use Finnish names — fuzzy match should work.
