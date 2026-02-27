# ADR-002: Finna REST API as primary data source

**Status:** Accepted
**Date:** 2026-02-27

## Context
Need a data source for Helmet library materials and their locations.

## Decision
Use the public Finna REST API (`api.finna.fi/v1/`) with Helmet building filters.

## Rationale
- Public, no auth required, CORS enabled
- Covers the entire Helmet network (Helsinki, Espoo, Vantaa, Kauniainen)
- Supports search by author, title, format, and building (branch)
- Returns structured JSON with building hierarchy

## Known limitations
- No real-time item-level availability (on shelf / checked out)
- No opening hours (addressed by ADR-003)
- Not designed for bulk data extraction
