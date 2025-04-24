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
    """
    project_path = pathlib.Path(path)
    if not project_path.exists():
        raise FileNotFoundError(f"Path '{path}' does not exist")

    mypy_cmd = ["mypy"]
    config_path = pathlib.Path(path) / "mypy.ini"
    if not config_path.exists():
        parent_path = pathlib.Path(path).parent
        parent_config = parent_path / "mypy.ini"
        if parent_config.exists():
            config_path = parent_config

    if config_path.exists():
        mypy_cmd.extend(["--config-file", str(config_path)])

    if exclude:
        for exclude_path in exclude:
            mypy_cmd.append(f"--exclude={exclude_path}")
    elif not pathlib.Path(path).name == "tests":
        try:
            if os.path.isdir(os.path.join(path, "tests")):
                mypy_cmd.append("--exclude=tests/")
        except (FileNotFoundError, PermissionError):
            pass

    if disallow_untyped_defs:
        mypy_cmd.append("--disallow-untyped-defs")
    if disallow_incomplete_defs:
        mypy_cmd.append("--disallow-incomplete-defs")
    if args:
        mypy_cmd.extend(args)
    mypy_cmd.append(path)
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
        raise RuntimeError(f"mypy failed: {stderr_output}")
