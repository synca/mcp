"""MCP server tools for filesystem operations."""

from mcp.server.fastmcp import Context, FastMCP

from synca.mcp.common.types import ResultDict
from synca.mcp.fs_extra.tool.head import HeadTool
from synca.mcp.fs_extra.tool.tail import TailTool
from synca.mcp.fs_extra.tool.grep import GrepTool
from synca.mcp.fs_extra.tool.sed import SedTool

mcp = FastMCP("FS-Extra")


# TOOLS


@mcp.tool()
async def fs_head(
        ctx: Context,
        cwd: str,
        head_args: tuple[str, ...]) -> ResultDict:
    """Display the beginning of a file.

    Wraps the Unix 'head' command to display the first part of files.
    Supports all options from the head command through direct argument
    passthrough.

    Note:
      For platform-specific information, use args=["--help"] or
      args=["--version"] as behavior and available options may vary across
      systems.

    Common usages:
      - Basic usage: pass args=["-n", "20", "filename.txt"] to see first 20
        lines
      - Byte limits: pass args=["-c", "1000", "filename.txt"] to see first
        1000 bytes

    Args:
        cwd: Directory path from which to run the head command
             (working directory)
        head_args: list of arguments to pass directly to the head
                   command.
                   These arguments are passed through exactly as provided
                   The file path should be included in the args parameter
                   See 'man head' for all available options

    Returns:
        A dictionary with the following structure:
        {
            "success": bool,
            "data": {
                "message": str,
                "output": str,
                "file_path": str,
                "lines_read": int,
                "bytes_read": int,
                "info": dict
            },
            "error": str | None
        }
    """
    return await HeadTool(ctx, cwd, dict(args=head_args)).run()


@mcp.tool()
async def fs_tail(
        ctx: Context,
        cwd: str,
        tail_args: tuple[str, ...]) -> ResultDict:
    """Display the end of a file.

    Wraps the Unix 'tail' command to display the last part of files.
    Supports all options from the tail command through direct argument
    passthrough.

    Note:
      For platform-specific information, use args=["--help"] or
      tail_args=["--version"] as behavior and available options may vary across
      systems.

    Common usages:
      - Basic usage: pass args=["-n", "20", "filename.txt"] to see last 20
        lines
      - Byte limits: pass args=["-c", "1000", "filename.txt"] to see last
        1000 bytes
      - Follow mode: pass args=["-f", "filename.txt"] to follow file updates

    Args:
        cwd: Directory path from which to run the tail command
              (working directory)
        tail_args: list of arguments to pass directly to the tail
                   command.
                   These arguments are passed through exactly as provided
                   The file path should be included in the args parameter
                   See 'man tail' for all available options

    Returns:
        A dictionary with the following structure:
        {
            "success": bool,
            "data": {
                "message": str,
                "output": str,
                "file_path": str,
                "lines_read": int,
                "bytes_read": int,
                "info": dict
            },
            "error": str | None
        }
    """
    return await TailTool(ctx, cwd, dict(args=tail_args)).run()


@mcp.tool()
async def fs_grep(
        ctx: Context,
        cwd: str,
        grep_args: tuple[str, ...]) -> ResultDict:
    """Search for patterns in a file or directory.

    Wraps the Unix 'grep' command to search for patterns in files.
    Supports all options from the grep command through direct argument
    passthrough.

    Note:
      For platform-specific information, use args=["--help"] or
      args=["--version"] as behavior and available options may vary across
      systems.

    Common usages:
      - Basic search: pattern="error", args=["filename.txt"] to find "error"
        in a file
      - Case-insensitive: args=["-i", "filename.txt"] for case-insensitive
        search
      - Context lines: args=["-C", "3", "filename.txt"] to show 3 lines
        before and after each match
      - Recursive search: args=["-r", "directory"] to search recursively
        in directories
      - Regular expressions: pattern can be a regular expression supported
        by grep

    Args:
        cwd: Directory path from which to run the grep command
              (working directory)
        grep_args: list of arguments to pass directly to the grep command
                   These arguments are passed through exactly as provided
                   The file or directory to search should be included in the
                   args parameter

    Returns:
        A dictionary with the following structure:
        {
            "success": bool,
            "data": {
                "message": str,
                "output": str,
                "match_count": int,
                "file_count": int,
                "info": dict
            },
            "error": str | None
        }
    """
    return await GrepTool(ctx, cwd, dict(args=grep_args)).run()


@mcp.tool()
async def fs_sed(
        ctx: Context,
        cwd: str,
        sed_args: tuple[str, ...]) -> ResultDict:
    """Perform text transformations on a file.

    Wraps the Unix 'sed' command to transform text in files and extract content.
    Can be used for line extraction, text substitution, and other
    transformations.
    Supports all options from the sed command through direct argument
    passthrough.

    Note:
      Some features may be platform/version dependent.
      For platform-specific information, use args=["--help"] or
      args=["--version"] as behavior and available options may vary across
      systems.

    Common usages:
      - Extract specific lines: args=["-n", "10,20p", "filename.txt"] to extract
        lines 10 through 20
      - Delete trailing whiepsace: args=["-e", "s/[[:space:]]*$//"]
      - Basic substitution: expression="s/old/new/g", args=["filename.txt"]
        to replace all occurrences
      - In-place editing: args=["-i", "filename.txt"] to edit the file
        in place
      - Backup while editing: args=["-i.bak", "filename.txt"] to create a backup
        with .bak extension
      - Delete lines: expression="10,20d", args=["filename.txt"] to delete
        lines 10-20

    Args:
        cwd: Directory path from which to run the sed command
              (working directory)
        sed_args: list of arguments to pass directly to the sed command
                  These arguments are passed through exactly as provided
                  The file path should be included in the args parameter
                  See 'man sed' for all available options

    Returns:
        A dictionary with the following structure:
        {
            "success": bool,
            "data": {
                "message": str,
                "output": str,
                "project_path": str,
                "info": dict
            },
            "error": str | None
        }
    """
    return await SedTool(ctx, cwd, dict(args=sed_args)).run()
