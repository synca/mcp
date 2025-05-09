"""Tail tool implementation for MCP server."""

from synca.mcp.fs_extra.tool.base import UnixSliceTool


class TailTool(UnixSliceTool):
    """Tail tool implementation using Unix tail command.

    This tool displays the end of a file using the Unix 'tail' command.
    It follows the direct argument passthrough pattern, allowing all tail
    options to be used including -f for following file changes.

    Note:
        The file path to process should be included as part of the args
        parameter.
    """
    success_message = "Successfully read the end of file"
    flags_with_args = ('-n', '--lines', '-c', '--bytes', '-f', '--follow')

    @property
    def tool_name(self) -> str:
        """Return the name of the tool."""
        return "tail"
