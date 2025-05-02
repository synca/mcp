"""Grep tool implementation for MCP server."""

from synca.mcp.fs_extra.tool.base import UnixTool


class GrepTool(UnixTool):
    """Grep tool implementation using Unix grep command."""

    @property
    def tool_name(self) -> str:
        """Return the name of the tool."""
        return "grep"
