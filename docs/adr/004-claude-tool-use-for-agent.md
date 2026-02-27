# ADR-004: Claude tool-use for agent orchestration

**Status:** Superseded by [ADR-005](005-mcp-server-as-delivery.md)
**Date:** 2026-02-27

## Context
Need an LLM layer to parse natural-language prompts into API calls and synthesize responses.

## Decision
Use Claude API with tool-use via the Anthropic Python SDK.

## Rationale
- Native tool-use support with structured input/output schemas
- Agent can decide which tools to call and in what order
- Handles multi-step reasoning (e.g. resolve branch name, then search, then format)
- System prompt guides decomposition of user questions

## Tools to expose
- `search_materials` — search Finna by query, author, format, branch
- `get_record_detail` — fetch full record info
- `list_library_branches` — discover available branches
- `get_opening_hours` — fetch schedules from Kirkanta
