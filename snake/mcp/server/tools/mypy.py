"""Mypy type checker tool implementation for MCP server."""

import os
import pathlib
import asyncio
from typing import Any
from mcp.server.fastmcp import Context


async def run_mypy(
        ctx: Context, path: str,
        args: list[str] | None = None,
        disallow_untyped_defs: bool = False,
        disallow_incomplete_defs: bool = False,
        exclude: list[str] | None = None) -> dict[str, Any]:
    """Run mypy type checker on a Python project.

    Executes mypy type checker on the specified project path.

    Args:
        ctx: MCP context
        path: Path to a Python project
        args: Optional list of additional arguments to pass to mypy
        disallow_untyped_defs: Whether to disallow functions without type
            annotations
        disallow_incomplete_defs: Whether to disallow functions with partial
            type annotations
        exclude: Optional list of directories/files to exclude from type
            checking

    Returns:
        A dictionary with the operation results
    """
    # Validate the path exists
    project_path = pathlib.Path(path)
    if not project_path.exists():
        raise FileNotFoundError(f"Path '{path}' does not exist")

    # Build the command
    mypy_cmd = ["mypy"]
    # Check if mypy.ini exists in the project root and use it
    config_path = pathlib.Path(path) / "mypy.ini"
    if not config_path.exists():
        # Try to find mypy.ini in parent directories
        parent_path = pathlib.Path(path).parent
        parent_config = parent_path / "mypy.ini"
        if parent_config.exists():
            config_path = parent_config

    if config_path.exists():
        mypy_cmd.extend(["--config-file", str(config_path)])

    # Add exclude directories if specified
    if exclude:
        for exclude_path in exclude:
            mypy_cmd.append(f"--exclude={exclude_path}")
    # Default exclude tests/ directory if not explicitly checking tests
    elif not pathlib.Path(path).name == "tests":
        try:
            if os.path.isdir(os.path.join(path, "tests")):
                mypy_cmd.append("--exclude=tests/")
        except (FileNotFoundError, PermissionError):
            pass

    # Add disallow_untyped_defs if specified
    if disallow_untyped_defs:
        mypy_cmd.append("--disallow-untyped-defs")
    # Add disallow_incomplete_defs if specified
    if disallow_incomplete_defs:
        mypy_cmd.append("--disallow-incomplete-defs")
    # Add any additional user arguments
    if args:
        mypy_cmd.extend(args)
    # Add the path
    mypy_cmd.append(path)
    # Run mypy with arguments
    process = await asyncio.create_subprocess_exec(
        *mypy_cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    stdout, stderr = await process.communicate()
    stderr_output = stderr.decode()
    stdout_output = stdout.decode()
    combined_output = stdout_output + "\n" + stderr_output
    # Count the number of issues (one per line in stdout with an error)
    issue_lines = [line for line in stdout_output.strip().splitlines()
                   if ': error:' in line or ': note:' in line]
    issues_count = len(issue_lines)
    has_issues = issues_count > 0
    # Prepare output and message
    strip_out = combined_output.strip()
    msg_output = strip_out if strip_out else "No issues found"
    # mypy returns 0 when no issues, 1 when issues found
    if process.returncode == 0 or process.returncode == 1:
        has_issues_msg = f"Found {issues_count} type issues"
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
        # Actual error running mypy
        raise RuntimeError(f"mypy failed: {stderr_output}")
