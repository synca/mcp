"""Base Tool class for Unix file tools."""

from synca.mcp.common.tool import CLITool
from synca.mcp.common.types import OutputTuple


class UnixTool(CLITool):
    """Base class for Unix filesystem tools.

    This base class implements the direct argument passthrough pattern
    for Unix command wrappers. It handles proper command construction
    and path validation.

    Note:
        The 'path' parameter represents the working directory from which to run
        the command, not the file to process. The file to process should be
        included n the args parameter.
    """
    failure_message = ""
    success_message = ""

    def parse_output(
            self,
            stdout: str,
            stderr: str,
            return_code: int) -> OutputTuple:
        """Parse the output of the head command.
        """
        if return_code != 0:
            return (
                return_code,
                self.failure_message,
                stderr if stderr else "Unknown error occurred",
                {})
        line_count = stdout.count('\n')
        return (
            return_code or 0,
            self.success_message,
            stdout,
            dict(lines_read=(
                     line_count + 1
                     if (stdout
                         and not stdout.endswith('\n'))
                     else line_count),
                 bytes_read=len(stdout.encode('utf-8'))))


class UnixSliceTool(UnixTool):
    success_message = "Command succeeded"
