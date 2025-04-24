"""Pytest tool implementation for MCP server."""

import pathlib
import asyncio
from typing import Any
from mcp.server.fastmcp import Context
from snake.mcp.server.tools.coverage import parse_coverage_data


async def run_pytest(
        ctx: Context, path: str,
        args: list[str] | None = None,
        verbose: bool = False,
        coverage: bool = False,
        coverage_source: str | None = None) -> dict[str, Any]:
    """Run pytest on a Python project.

    Executes pytest test runner on the specified project path.

    Args:
        ctx: MCP context
        path: Path to a Python project
        args: Optional list of additional arguments to pass to pytest
        verbose: Whether to run pytest in verbose mode (-v)
        coverage: Whether to run with coverage reporting
        coverage_source: Source directory or package to measure coverage for

    Returns:
        A dictionary with the operation results and test summary
    """
    # Validate the path exists
    project_path = pathlib.Path(path)
    if not project_path.exists():
        raise FileNotFoundError(f"Path '{path}' does not exist")

    # Build the command
    pytest_cmd = ["pytest"]
    # Add verbose flag if specified
    if verbose:
        pytest_cmd.append("-v")
    # Add coverage options if specified
    coverage_data = None
    if coverage:
        # Add basic coverage flag
        if coverage_source:
            pytest_cmd.append(f"--cov={coverage_source}")
        else:
            pytest_cmd.append("--cov")
        # Add some default coverage options for better reporting
        pytest_cmd.append("--cov-report=term")
    # Add any additional user arguments
    if args:
        pytest_cmd.extend(args)
    # Run pytest with arguments
    process = await asyncio.create_subprocess_exec(
        *pytest_cmd,
        cwd=path,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    stdout, stderr = await process.communicate()
    stderr_output = stderr.decode()
    stdout_output = stdout.decode()
    combined_output = stdout_output + "\n" + stderr_output
    # Parse test results to provide more structured information
    test_summary = parse_test_summary(combined_output)

    # Parse coverage information if coverage was enabled
    coverage_data = None
    if coverage:
        coverage_data = parse_coverage_data(combined_output)

    if process.returncode == 0:
        return {
            "success": True,
            "data": {
                "message": "All tests passed successfully",
                "output": combined_output,
                "project_path": path,
                "test_summary": test_summary,
                "coverage": coverage_data
            },
            "error": None
        }
    else:
        # pytest returns non-zero when tests fail, but this isn't an error
        # in our tool's execution - the tool successfully ran the tests
        return {
            "success": True,
            "data": {
                "message": "Some tests failed",
                "output": combined_output,
                "project_path": path,
                "test_summary": test_summary,
                "coverage": coverage_data
            },
            "error": None
        }


def parse_test_summary(output: str) -> dict[str, int]:
    """Parse the test summary from pytest output.

    Args:
        output: The combined stdout and stderr output from pytest

    Returns:
        A dictionary with test result counts
    """
    test_summary = {
        "total": 0,
        "passed": 0,
        "failed": 0,
        "skipped": 0,
        "xfailed": 0,
        "xpassed": 0
    }
    # Look for the summary line usually at the end of pytest output
    try:
        for line in output.splitlines():
            if ("=" in line) and any(x in line for x in [
                    "passed", "failed", "skipped", "xfailed",
                    "xpassed"]):
                # Parse summary like "= 4 passed, 2 failed ="
                # or "===== 2 passed in 0.01s ===="
                line = line.strip("=").strip()
                # Handle the part before "in X.XXs" with test counts
                if " in " in line:
                    line = line.split(" in ")[0].strip()
                parts = line.split(",")
                for part in parts:
                    part = part.strip()
                    if not part:
                        continue
                    # Extract counts handling formats
                    try:
                        if "passed" in part and "xpassed" not in part:
                            test_summary["passed"] = int(part.split()[0])
                        elif "failed" in part and "xfailed" not in part:
                            test_summary["failed"] = int(part.split()[0])
                        elif "skipped" in part:
                            test_summary["skipped"] = int(part.split()[0])
                        elif "xfailed" in part:
                            test_summary["xfailed"] = int(part.split()[0])
                        elif "xpassed" in part:
                            test_summary["xpassed"] = int(part.split()[0])
                    except (ValueError, IndexError):
                        # Skip if we can't parse this part
                        continue

                # Calculate total
                test_summary["total"] = (
                    test_summary["passed"] +
                    test_summary["failed"] +
                    test_summary["skipped"] +
                    test_summary["xfailed"] +
                    test_summary["xpassed"]
                )
                break
    except Exception:
        # If there's any error in parsing, just continue with zeros
        pass

    return test_summary
