"""Sed tool implementation for MCP server."""

from synca.mcp.fs_extra.tool.base import UnixTool


class SedTool(UnixTool):
    """Sed tool implementation using Unix sed command."""
    success_message = "Successfully ran the sed command"

    @property
    def tool_name(self) -> str:
        """Return the name of the tool."""
        return "sed"
