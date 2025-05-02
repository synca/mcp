"""Flake8 linter tool implementation for MCP server."""

from synca.mcp.python.tool.base import PythonTool


class Flake8Tool(PythonTool):
    """Flake8 linter tool implementation."""

    @property
    def tool_name(self) -> str:
        return "flake8"
