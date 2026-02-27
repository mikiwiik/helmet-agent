# API Reference

External APIs used by the Helmet library agent.

---

## Finna API

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
| `filter[]` | `building:"2/Helmet/h/h33/"` | Restrict to specific branch (e.g. Munkkiniemi) |
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
- `2/Helmet/h/h01/` — Pasila, `2/Helmet/h/h33/` — Munkkiniemi, etc.

Branch codes (level 2) are maintained as a static lookup table in `branch_resolver.py`.

**Important:** When filtering by branch, use the branch code alone — do NOT combine with `0/Helmet/`. The `~building` (tilde/OR) prefix makes the filter ineffective when combined with the top-level code.

### Record Fields

Records return: `id`, `title`, `authors`, `formats`, `buildings` (which branches hold it), `year`, `languages`, `subjects`, `images`, `series`, `rating`

### What the API does NOT provide

- **Real-time item-level availability** (on shelf / checked out) — the `buildings` field shows which branches have the item in their collection, but not current loan status
- **Opening hours** — not available via the search/record API; use Kirkanta API instead

---

## Kirkanta API

- **Base URL:** `https://api.kirjastot.fi/v4/`
- **Auth:** None required
- **Key endpoint:** `GET /v4/library?city.name=helsinki&with=schedules`
- Returns: name, address, coordinates, opening hours, contact info
- 92 Helsinki municipal libraries indexed
