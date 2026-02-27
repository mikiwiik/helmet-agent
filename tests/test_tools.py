"""Integration tests for MCP tool functions."""

from helmet_agent.server import mcp


def test_server_has_name():
    assert mcp.name == "helmet-library"
