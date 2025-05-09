"""Sed tool implementation for MCP server."""

from synca.mcp.common.types import ArgTuple
from synca.mcp.fs_extra.errors import FSCommandError
from synca.mcp.fs_extra.tool.base import UnixTool


class SedTool(UnixTool):
    """Sed tool implementation using Unix sed command."""
    success_message = "Successfully ran the sed command"
    flags_with_args = ('-e', '--expression', '-f', '--file')

    @property
    def tool_name(self) -> str:
        """Return the name of the tool."""
        return "sed"

    def validate_args(self, args: ArgTuple) -> None:
        """Check if sed arguments include at least one file path.

        Sed will wait for stdin if no file is specified, which would
        cause the process to hang in this context.
        """
        invalid = (
            not args
            or (len(args) < 2
                and not args[0].startswith('-')))
        if invalid:
            raise FSCommandError(self.err_stdin)
        for i, arg in enumerate(args):
            if arg in ('-f', '--file') and i + 1 < len(args):
                return None
        if not self.has_path_arg(args):
            raise FSCommandError(self.err_stdin)
