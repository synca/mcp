"""MCP server tools for Python."""

from mcp.server.fastmcp import Context, FastMCP

from synca.mcp.common.types import ResultDict
from synca.mcp.python.tool.pytest import PytestTool
from synca.mcp.python.tool.mypy import MypyTool
from synca.mcp.python.tool.flake8 import Flake8Tool

mcp = FastMCP("Python")

# TOOL


@mcp.tool()
async def pytest(
        ctx: Context,
        cwd: str,
        pytest_args: tuple[str, ...] | None = None) -> ResultDict:
    """Run pytest on a Python project

    Executes pytest test runner on the specified project path.

    Args:
        cwd: Directory path from which to run pytest (working directory)
        pytest_args: Optional list of additional arguments to pass to pytest

    Returns:
        A dictionary with the following structure:
        {
            "success": bool,
            "data": {
                "message": str,
                "output": str,
                "project_path": str,
                "test_summary": {
                    "total": int,
                    "passed": int,
                    "failed": int,
                    "skipped": int,
                    "xfailed": int,
                    "xpassed": int
                },
                "coverage": {
                    "total": float,
                    "by_file": dict
                }
            },
            "error": str | None
        }
    """
    return await PytestTool(ctx, cwd, dict(args=pytest_args)).run()


@mcp.tool()
async def mypy(
        ctx: Context,
        cwd: str,
        mypy_args: tuple[str, ...] | None = None) -> ResultDict:
    """Run mypy type checker on a Python project

    Executes mypy type checker on the specified project path.

    Args:
        cwd: Directory path from which to run mypy (working directory)
        mypy_args: Optional list of additional arguments to pass to mypy
             Examples: ["--no-implicit-optional", "--disallow-untyped-defs",
                        "--disallow-incomplete-defs"]

    Returns:
        A dictionary with the following structure:
        {
            "success": bool,
            "data": {
                "message": str,
                "output": str,
                "project_path": str,
                "issues_count": int,
                "has_issues": bool
            },
            "error": str | None
        }
    """
    return await MypyTool(ctx, cwd, dict(args=mypy_args)).run()


@mcp.tool()
async def flake8(
        ctx: Context,
        cwd: str,
        flake8_args: tuple[str, ...] | None = None) -> ResultDict:
    """Run flake8 linter on a Python project

    Executes flake8 linter on the specified project path.

    Args:
        path: Directory path from which to run flake8 (working directory)
        flake8_args: Optional list of additional arguments to pass to flake8
             Examples: ["--ignore=E203", "--exclude=.git"]

    Returns:
        A dictionary with the following structure:
        {
            "success": bool,
            "data": {
                "message": str,
                "output": str,
                "project_path": str,
                "issues_count": int,
                "has_issues": bool
            },
            "error": str | None
        }

    """
    return await Flake8Tool(ctx, cwd, dict(args=flake8_args)).run()
