"""Flake8 linter tool implementation for MCP server."""

import pathlib
import asyncio
from typing import Any
from mcp.server.fastmcp import Context


async def run_flake8(
        ctx: Context, path: str,
        args: list[str] | None = None,
        max_line_length: int | None = None) -> dict[str, Any]:
    """Run flake8 linter on a Python project.

    Executes flake8 linter on the specified project path.

    Args:
        ctx: MCP context
        path: Path to a Python project
        args: Optional list of additional arguments to pass to flake8
        max_line_length: Optional maximum line length to enforce

    Returns:
        A dictionary with the operation results
    """
    # Validate the path exists
    project_path = pathlib.Path(path)
    if not project_path.exists():
        raise FileNotFoundError(f"Path '{path}' does not exist")

    # Build the command
    flake8_cmd = ["flake8"]
    # Add max line length if specified
    if max_line_length is not None:
        flake8_cmd.append(f"--max-line-length={max_line_length}")
    # Add any additional user arguments
    if args:
        flake8_cmd.extend(args)
    # Add the path
    flake8_cmd.append(path)
    # Run flake8 with arguments
    process = await asyncio.create_subprocess_exec(
        *flake8_cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    stdout, stderr = await process.communicate()
    stderr_output = stderr.decode()
    stdout_output = stdout.decode()
    combined_output = stdout_output + "\n" + stderr_output
    # Count the number of issues (one per line in stdout)
    stdout_length = len(stdout_output.strip().splitlines())
    issues_count = stdout_length if stdout_output.strip() else 0
    has_issues = issues_count > 0
    # Prepare output and message
    strip_out = combined_output.strip()
    msg_output = strip_out if strip_out else "No issues found"
    # flake8 returns 0 when no issues, 1 when issues found
    if process.returncode == 0 or process.returncode == 1:
        has_issues_msg = f"Found {issues_count} issues"
        message = "No issues found" if not has_issues else has_issues_msg
        return {
            "success": True,
            "data": {
                "message": message,
                "output": msg_output,
                "project_path": path,
                "issues_count": issues_count,
                "has_issues": has_issues
            },
            "error": None
        }
    else:
        # Actual error running flake8
        raise RuntimeError(f"flake8 failed: {stderr_output}")
