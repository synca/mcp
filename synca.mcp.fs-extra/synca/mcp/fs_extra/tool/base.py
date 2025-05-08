"""Base Tool class for Unix file tools."""

from synca.mcp.common.tool import CLITool
from synca.mcp.common.types import ArgTuple, OutputTuple
from synca.mcp.fs_extra.errors import FSCommandError


class UnixTool(CLITool):
    """Base class for Unix filesystem tools.
    """
    failure_message = ""
    success_message = ""
    flags_with_args: tuple[str, ...] = ()

    @property
    def args(self) -> ArgTuple:
        """Return the validated arguments for the tool command.
        """
        args = super().args
        self.validate_args(args)
        return args

    @property
    def err_stdin(self) -> str:
        return (
            f"{self.tool_name.capitalize()} command requires file "
            "arguments. The command might be expecting input from stdin, "
            "which is not supported. "
            "Please provide at least one explicit file path in your "
            f"{self.tool_name} command.")

    def has_path_arg(self, args: ArgTuple) -> bool:
        skip_next = False
        for arg in args:
            if skip_next:
                skip_next = False
                continue
            if arg in self.flags_with_args:
                skip_next = True
                continue
            if not arg.startswith('-'):
                return True
        return False

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

    def validate_args(self, args: ArgTuple) -> None:
        """Validate command line arguments.
        """
        return None


class UnixSliceTool(UnixTool):
    success_message = "Command succeeded"

    def validate_args(self, args: ArgTuple) -> None:
        """Validate command line arguments.
        """
        if not args:
            raise FSCommandError(self.err_stdin)
        if self.has_path_arg(args):
            return
        raise FSCommandError(self.err_stdin)
