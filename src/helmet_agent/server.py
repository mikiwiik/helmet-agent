"""Helmet library MCP server entry point."""

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("helmet-library")


def main() -> None:
    import helmet_agent.tools  # noqa: F401 — registers tools with mcp

    mcp.run()


if __name__ == "__main__":
    main()
