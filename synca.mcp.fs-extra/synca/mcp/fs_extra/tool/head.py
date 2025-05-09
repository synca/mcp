"""Head tool implementation for MCP server."""

from synca.mcp.fs_extra.tool.base import UnixSliceTool


class HeadTool(UnixSliceTool):
    """Head tool implementation using Unix head command.

    This tool displays the beginning of a file using the Unix 'head' command.
    It follows the direct argument passthrough pattern, allowing all head
    options to be used.

    Note:
        The file path to process should be included as part of the args
        parameter.
    """
    success_message = "Successfully read the beginning of file"
    flags_with_args = ('-n', '--lines', '-c', '--bytes')

    @property
    def tool_name(self) -> str:
        """Return the name of the tool."""
        return "head"
