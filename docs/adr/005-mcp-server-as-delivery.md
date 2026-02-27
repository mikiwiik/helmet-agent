# ADR-005: MCP server as delivery mechanism

**Status:** Accepted (supersedes ADR-004)
**Date:** 2026-02-27

## Context
Need to decide how users interact with the agent. Options considered: standalone CLI, web app, chat bot, MCP server.

## Decision
Build the tools as an MCP server using the `mcp` Python SDK (`FastMCP`). Claude Code / Claude Desktop acts as the host — no custom agent orchestration needed.

## Rationale
- User already uses Claude Code daily — zero friction to adopt
- Claude handles all reasoning, decomposition, and response formatting natively
- We only implement the tools, not the orchestration layer
- MCP is a standard protocol — server works with any MCP-compatible host
- Dramatically simpler architecture: no `anthropic` SDK dependency, no system prompt management

## Consequences
- ADR-004 (Claude tool-use orchestration) is superseded — Claude handles this as the MCP host
- No need for `agent.py` or custom system prompts
- Server runs via stdio transport, configured in Claude Code settings
- Dependencies reduce to: `mcp`, `httpx`
