# ADR-003: Kirkanta API for opening hours

**Status:** Accepted
**Date:** 2026-02-27

## Context
Finna API does not provide library opening hours. Users will ask "When is X library open?"

## Decision
Use the Kirkanta API (`api.kirjastot.fi/v4/`) for library metadata and schedules.

## Rationale
- Public, no auth required
- Covers all Finnish public libraries including all Helmet branches
- Provides opening hours via `?with=schedules` parameter
- Returns address, coordinates, contact info
- Verified working: 92 Helsinki municipal libraries indexed

## Notes
- Need to map between Finna branch names and Kirkanta library IDs/names
- Kirkanta uses `city.name=helsinki` parameter format
