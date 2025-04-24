"""MCP server tools for Python."""

import traceback

from mcp.server.fastmcp import Context, FastMCP
from snake.mcp.server.tools.pytest import run_pytest
from snake.mcp.server.tools.mypy import run_mypy
from snake.mcp.server.tools.flake8 import Flake8Tool

mcp = FastMCP("Python")

# TOOLS


@mcp.tool()
async def pytest(
        ctx: Context, path: str,
        args: list[str] | None = None,
        verbose: bool = False,
        coverage: bool = False,
        coverage_source: str | None = None) -> dict:
    """Run pytest on a Python project

    Executes pytest test runner on the specified project path.

    Args:
        path: Path to a Python project
        args: Optional list of additional arguments to pass to pytest
             Examples: ["-xvs", "--cov=mypackage", "--no-cov-on-fail"]
        verbose: Whether to run pytest in verbose mode (-v)
        coverage: Whether to run with coverage reporting
        coverage_source: Source directory or package to measure coverage for
             Example: "mypackage" or "src"

    Returns:
        A dictionary with the following structure:
        {
            "success": bool,  # Whether operation completed successfully
            "data": {        # Present only if success is True
                "message": str,  # Summary
                "output": str,   # Output
                "project_path": str,  # Path
                "test_summary": {
                    "total": int,
                    "passed": int,
                    "failed": int,
                    "skipped": int,
                    "xfailed": int,
                    "xpassed": int
                },
                "coverage": {  # Present only if coverage=True and successful
                    "total": float,  # Total coverage percentage
                    "by_file": dict  # Coverage by file
                }
            },
            "error": str | None  # Error message if failure
        }
    """
    try:
        return await run_pytest(
            ctx, path, args, verbose, coverage, coverage_source)
    except Exception as e:
        trace = traceback.format_exc()
        return {
            "success": False,
            "data": None,
            "error": f"Failed to run pytest: {str(e)}\n{trace}"
        }


@mcp.tool()
async def mypy(
        ctx: Context, path: str,
        args: list[str] | None = None,
        disallow_untyped_defs: bool = False,
        disallow_incomplete_defs: bool = False,
        exclude: list[str] | None = None) -> dict:
    """Run mypy type checker on a Python project

    Executes mypy type checker on the specified project path.

    Args:
        path: Path to a Python project
        args: Optional list of additional arguments to pass to mypy
             Examples: ["--no-implicit-optional"]
        disallow_untyped_defs: Whether to disallow functions without type
            annotations
        disallow_incomplete_defs: Whether to disallow functions with partial
            type annotations
        exclude: Optional list of directories/files to exclude from type
            checking
             Example: ["tests/"]

    Returns:
        A dictionary with the following structure:
        {
            "success": bool,  # Whether operation completed successfully
            "data": {        # Present only if success is True
                "message": str,
                "output": str,
                "project_path": str,
                "issues_count": int,
                "has_issues": bool
            },
            "error": str | None  # Error message if failure
        }
    """
    try:
        return await run_mypy(
            ctx, path, args, disallow_untyped_defs,
            disallow_incomplete_defs, exclude)
    except Exception as e:
        trace = traceback.format_exc()
        return {
            "success": False,
            "data": None,
            "error": f"Failed to run mypy: {str(e)}\n{trace}"
        }


@mcp.tool()
async def flake8(
        ctx: Context, path: str,
        args: list[str] | None = None,
        max_line_length: int | None = None) -> dict:
    """Run flake8 linter on a Python project

    Executes flake8 linter on the specified project path.

    Args:
        path: Path to a Python project
        args: Optional list of additional arguments to pass to flake8
             Examples: ["--ignore=E203", "--exclude=.git"]
        max_line_length: Optional maximum line length to enforce

    Returns:
        A dictionary with the following structure:
        {
            "success": bool,  # Whether operation completed successfully
            "data": {        # Present only if success is True
                "message": str,
                "output": str,
                "project_path": str,
                "issues_count": int,
                "has_issues": bool
            },
            "error": str | None  # Error message if failure
        }
    """
    flake8_tool = Flake8Tool()
    return await flake8_tool.run(ctx, path, args, max_line_length)
