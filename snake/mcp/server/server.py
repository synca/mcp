import pathlib
import os
import asyncio
from mcp.server.fastmcp import Context, FastMCP

mcp = FastMCP("Python")

# TOOLS


@mcp.tool()
async def pytest(ctx: Context, path: str,
                 args: list[str] | None = None,
                 verbose: bool = False,
                 coverage: bool = False,
                 coverage_source: str | None = None) -> dict:
    """Run pytest on a Python project

    Executes pytest test runner on the specified project path.

    Args:
        path: Path to a Python project
        args: Optional list of additional arguments to pass to pytest
             Examples: ["-xvs", "--cov=mypackage",
                       "--no-cov-on-fail"]
        verbose: Whether to run pytest in verbose mode (-v)
        coverage: Whether to run with coverage reporting
        coverage_source: Source directory or package to measure coverage for
             Example: "mypackage" or "src"

    Returns:
        A dictionary with the following structure:
        {
            "success": bool,  # Whether the operation completed successfully
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
    # Validate the path exists
    project_path = pathlib.Path(path)
    if not project_path.exists():
        return {
            "success": False,
            "data": None,
            "error": f"Path '{path}' does not exist"
        }
    try:
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
            for line in combined_output.splitlines():
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

        # Parse coverage information if coverage was enabled
        coverage_data = None
        if coverage:
            coverage_data = {
                "total": 0.0,
                "by_file": {}
            }
            try:
                # Look for the coverage table format:
                # Name                           Stmts   Miss  Cover
                # --------------------------------------------------
                # snake/__init__.py                  0      0   100%
                # TOTAL                            444     49    89%
                in_coverage_table = False
                for line in combined_output.splitlines():
                    # Identify the start of coverage table (header line)
                    if ("Name" in line and "Stmts" in line and
                            "Miss" in line and "Cover" in line):
                        in_coverage_table = True
                        continue
                    # Skip separator line after header
                    if in_coverage_table and line.strip().startswith('-'):
                        continue
                    # End of table
                    if (in_coverage_table and
                            ("==" in line or not line.strip())):
                        in_coverage_table = False
                        continue
                    # Process table rows
                    if in_coverage_table and line.strip():
                        parts = line.split()
                        if len(parts) >= 4:
                            # Check if we have a valid coverage value
                            cov_string = parts[-1]
                            if cov_string.endswith("%"):
                                try:
                                    file_path = parts[0]
                                    cov_value = float(cov_string.rstrip("%"))

                                    # Check if this is the TOTAL line
                                    if file_path == "TOTAL":
                                        coverage_data["total"] = cov_value
                                    else:
                                        if isinstance(
                                                coverage_data["by_file"], dict
                                        ):
                                            coverage_data["by_file"][
                                                file_path
                                            ] = cov_value
                                except (ValueError, IndexError):
                                    # Skip if we can't parse
                                    pass
            except Exception:
                # If there's any error in parsing, just continue
                pass

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
    except Exception as e:
        return {
            "success": False,
            "data": None,
            "error": f"Failed to run pytest: {str(e)}"
        }


@mcp.tool()
async def mypy(ctx: Context, path: str,
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
            "success": bool,  # Whether the operation completed successfully
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
    # Validate the path exists
    project_path = pathlib.Path(path)
    if not project_path.exists():
        return {
            "success": False,
            "data": None,
            "error": f"Path '{path}' does not exist"
        }
    try:
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
            return {
                "success": False,
                "data": None,
                "error": f"mypy failed: {stderr_output}"
            }
    except Exception as e:
        return {
            "success": False,
            "data": None,
            "error": f"Failed to run mypy: {str(e)}"
        }


@mcp.tool()
async def flake8(ctx: Context, path: str,
                 args: list[str] | None = None,
                 max_line_length: int | None = None) -> dict:
    """Run flake8 linter on a Python project

    Executes flake8 linter on the specified project path.

    Args:
        path: Path to a Python project
        args: Optional list of additional arguments to pass to flake8
             Examples: ["--ignore=E203",
                       "--exclude=.git"]
        max_line_length: Optional maximum line length to enforce

    Returns:
        A dictionary with the following structure:
        {
            "success": bool,  # Whether the operation completed successfully
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
    # Validate the path exists
    project_path = pathlib.Path(path)
    if not project_path.exists():
        return {
            "success": False,
            "data": None,
            "error": f"Path '{path}' does not exist"
        }
    try:
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
            return {
                "success": False,
                "data": None,
                "error": f"flake8 failed: {stderr_output}"
            }
    except Exception as e:
        return {
            "success": False,
            "data": None,
            "error": f"Failed to run flake8: {str(e)}"
        }
