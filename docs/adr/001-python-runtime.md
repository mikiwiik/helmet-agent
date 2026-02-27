# ADR-001: Python as runtime

**Status:** Accepted
**Date:** 2026-02-27

## Context
Need to choose between Python and TypeScript for the agent implementation.

## Decision
Python 3.12+, using `httpx` for async HTTP and `anthropic` SDK for Claude tool-use.

## Rationale
- Existing `finna-client` package (reference, even if we write our own wrapper)
- Anthropic Python SDK is mature and well-documented
- Rich ecosystem for text processing and fuzzy matching
- Simpler deployment for a CLI tool
