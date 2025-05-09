"""Grep tool implementation for MCP server."""

from synca.mcp.fs_extra.errors import FSCommandError
from synca.mcp.fs_extra.tool.base import UnixTool


class GrepTool(UnixTool):
    """Grep tool implementation using Unix grep command."""
    _recursive_flags = ('-r', '-R', '--recursive')

    @property
    def tool_name(self) -> str:
        """Return the name of the tool."""
        return "grep"

    def validate_args(self, args):
        """Check if grep arguments appear to be complete or might
        require stdin.
        """
        if not args:
            return
        has_recursive = any(
            arg
            in self._recursive_flags
            for arg
            in args)
        if has_recursive:
            return
        if self.has_path_arg(args):
            return
        raise FSCommandError(self.err_stdin)
