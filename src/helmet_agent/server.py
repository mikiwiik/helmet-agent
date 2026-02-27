"""Helmet library MCP server entry point."""

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("helmet-library")


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()
