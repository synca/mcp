"""Flake8 linter tool implementation for MCP server."""

import asyncio
import pathlib
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
    project_path = pathlib.Path(path)
    if not project_path.exists():
        raise FileNotFoundError(f"Path '{path}' does not exist")

    flake8_cmd = ["flake8"]
    if max_line_length is not None:
        flake8_cmd.append(f"--max-line-length={max_line_length}")
    if args:
        flake8_cmd.extend(args)
    flake8_cmd.append(path)
    process = await asyncio.create_subprocess_exec(
        *flake8_cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    stdout, stderr = await process.communicate()
    stderr_output = stderr.decode()
    stdout_output = stdout.decode()
    combined_output = stdout_output + "\n" + stderr_output
    stdout_length = len(stdout_output.strip().splitlines())
    issues_count = stdout_length if stdout_output.strip() else 0
    has_issues = issues_count > 0
    strip_out = combined_output.strip()
    msg_output = strip_out if strip_out else "No issues found"
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
        raise RuntimeError(f"flake8 failed: {stderr_output}")
