from mcp.server.fastmcp import Context, FastMCP

from synca.mcp.common.types import ResultDict
from synca.mcp.cargo.tool import (
    ClippyTool, BuildTool, CheckTool,
    FmtTool, TestTool, TarpaulinTool, RunTool)
from synca.mcp.cargo.tool.doc import DocTool

mcp = FastMCP("Cargo")


# TOOLS


@mcp.tool()
async def cargo_clippy(
        ctx: Context,
        cwd: str,
        clippy_args: tuple[str, ...] | None = None) -> ResultDict:
    """Run cargo clippy on a Rust project

    Executes clippy linter on the specified Rust project path.

    Args:
        cwd: Path to a Rust project containing a Cargo.toml file
        clippy_args: Optional list of additional arguments to pass to clippy
             Examples: ["--no-deps", "--workspace", "--", "-D", "warnings"]

    Returns:
        A dictionary with the following structure:
        {
            # Whether the operation completed successfully
            "success": bool,
            # Present only if success is True
            "data": {
                # Summary message about the result
                "message": str,
                # Combined stdout/stderr output from clippy
                "output": str,
                # Path to the project that was linted
                "project_path": str,
                # Number of issues found by clippy
                "issues_count": int,
                # Additional info parsed from tool response
                "info": dict
            },
            # Error message if success is False, otherwise None
            "error": str | None
        }
    """
    return await ClippyTool(ctx, cwd, dict(args=clippy_args)).run()


@mcp.tool()
async def cargo_check(
        ctx: Context,
        cwd: str,
        check_args: tuple[str, ...] | None = None) -> ResultDict:
    """Run cargo check on a Rust project

    Checks a package for errors without building it.

    Args:
        path: Path to a Rust project containing a Cargo.toml file
        args: Optional list of additional arguments to pass to cargo check
             Examples: ["--all-features", "--workspace", "--lib"]

    Returns:
        A dictionary with the following structure:
        {
            # Whether the operation completed successfully
            "success": bool,
            # Present only if success is True
            "data": {
                # Summary message about the result
                "message": str,
                # Combined stdout/stderr output
                "output": str,
                # Path to the project that was checked
                "project_path": str
            },
            # Error message if success is False, otherwise None
            "error": str | None
        }
    """
    return await CheckTool(ctx, cwd, dict(args=check_args)).run()


@mcp.tool()
async def cargo_build(
        ctx: Context,
        cwd: str,
        build_args: tuple[str, ...] | None = None) -> ResultDict:
    """Build a Rust project

    Compiles a package and all of its dependencies.

    Args:
        cwd: Path to a Rust project containing a Cargo.toml file
        build_args: Optional list of additional arguments to pass
                    to cargo build
             Examples: ["--release", "--workspace", "--all-features", "--lib"]

    Returns:
        A dictionary with the following structure:
        {
            # Whether the operation completed successfully
            "success": bool,
            # Present only if success is True
            "data": {
                # Summary message about the result
                "message": str,
                # Combined stdout/stderr output
                "output": str,
                # Path to the project that was built
                "project_path": str,
                # Either "debug" or "release"
                "build_mode": str
            },
            # Error message if success is False, otherwise None
            "error": str | None
        }
    """
    return await BuildTool(ctx, cwd, dict(args=build_args)).run()


@mcp.tool()
async def cargo_test(
        ctx: Context,
        cwd: str,
        test_args: tuple[str, ...] | None = None) -> ResultDict:
    """Run tests for a Rust project

    Executes all unit and integration tests for a package.

    Args:
        cwd: Path to a Rust project containing a Cargo.toml file
        test_args: Optional list of additional arguments to pass to cargo test
             Examples: ["--release", "--no-fail-fast", "--verbose"]
             Test name patterns can also be passed directly in args

    Returns:
        A dictionary with the following structure:
        {
            # Whether all tests passed
            "success": bool,
            # Present regardless of success
            "data": {
                # Summary message about the test results
                "message": str,
                # Combined stdout/stderr output from tests
                "output": str,
                # Path to the project that was tested
                "project_path": str,
                # Summary statistics about test results
                "test_summary": {
                    # Total number of tests run
                    "total_tests": int,
                    # Number of passing tests
                    "passed": int,
                    # Number of failing tests (if any)
                    "failed": int,
                    # Overall status: "passed" or "failed"
                    "status": str
                }
            },
            # Error message if success is False, otherwise None
            "error": str | None
        }
    """
    return await TestTool(ctx, cwd, dict(args=test_args)).run()


@mcp.tool()
async def cargo_fmt(
        ctx: Context,
        cwd: str,
        fmt_args: tuple[str, ...] | None = None) -> ResultDict:
    """Format Rust code using rustfmt

    Formats Rust code according to style guidelines using rustfmt.

    Args:
        cwd: Path to a Rust project containing a Cargo.toml file
        fmt_args: Optional list of additional arguments to pass to cargo fmt
             Examples:
                 ["--manifest-path=path/to/Cargo.toml", "--all", "--check"]

    Returns:
        A dictionary with the following structure:
        {
            # Whether the operation completed successfully
            "success": bool,
            # Present only if success is True
            "data": {
                # Summary message about the formatting status
                "message": str,
                # Whether code needs formatting
                "needs_formatting": bool,
                # Detailed output showing formatting differences (if any)
                "output": str,
                # Path to the project that was formatted
                "project_path": str
            },
            # Error message if success is False, otherwise None
            "error": str | None
        }
    """
    return await FmtTool(ctx, cwd, dict(args=fmt_args)).run()


@mcp.tool()
async def cargo_doc(
        ctx: Context,
        cwd: str,
        doc_args: tuple[str, ...] | None = None) -> ResultDict:
    """Generate documentation for a Rust project

    Builds documentation for the local package and all dependencies.

    Args:
        cwd: Path to a Rust project containing a Cargo.toml file
        doc_args: Optional list of additional arguments to pass to cargo doc
             Examples:
                 ["--no-deps", "--document-private-items", "--lib", "--open"]

    Returns:
        A dictionary with the following structure:
        {
            # Whether the operation completed successfully
            "success": bool,
            # Present only if success is True
            "data": {
                # Summary message about the documentation generation
                "message": str,
                # Combined stdout/stderr output from cargo doc
                "output": str,
                # Path to the project that was documented
                "project_path": str,
                # Path to the generated documentation root
                "doc_path": str,
                # Path to this specific package's docs
                "package_doc_path": str | None
            },
            # Error message if success is False, otherwise None
            "error": str | None
        }
    """
    return await DocTool(ctx, cwd, dict(args=doc_args)).run()


@mcp.tool()
async def cargo_run(
        ctx: Context,
        cwd: str,
        run_args: tuple[str, ...] | None = None) -> ResultDict:
    """Run a Rust project binary

    Compiles and runs the main binary or a specified binary.

    Args:
        path: Path to a Rust project containing a Cargo.toml file
        args: Optional list of arguments to pass to the binary
             These are arguments for the binary itself, not for cargo
             Can include flags like "--release" or "--bin=name" for cargo

    Returns:
        A dictionary with the following structure:
        {
            # Whether the execution completed successfully
            "success": bool,
            # Present only if success is True
            "data": {
                # Summary message about the execution
                "message": str,
                # Combined stdout/stderr from both compilation and program
                "output": str,
                # Cargo output during compilation
                "compilation_output": str | None,
                # Output from the executed program
                "program_output": str,
                # Path to the project that was run
                "project_path": str,
                # Name of the binary that was run, if specified
                "binary": str | None,
                # Either "release" or "debug"
                "mode": str
            },
            # Error message if success is False, otherwise None
            "error": str | None
        }
    """
    return await RunTool(ctx, cwd, dict(args=run_args)).run()


@mcp.tool()
async def cargo_tarpaulin(
        ctx: Context,
        cwd: str,
        tarpaulin_args: tuple[str, ...] | None = None) -> ResultDict:
    """Run code coverage analysis using cargo-tarpaulin

    Measures code coverage of tests in a Rust project.

    Args:
        cwd: Path to a Rust project containing a Cargo.toml file
        tarpaulin_args: Optional list of additional arguments to pass
                        to tarpaulin
          Examples:
            ["--workspace", "--exclude-files=**/tests/**", "--fail-under=80"]

    Returns:
        A dictionary with the following structure:
        {
            # Whether the coverage analysis completed successfully
            "success": bool,
            # Present only if success is True
            "data": {
                # Summary message about the coverage analysis
                "message": str,
                # Combined stdout/stderr output from tarpaulin
                "output": str,
                # Path to the project that was analyzed
                "project_path": str,
                # Coverage statistics and file information
                "coverage_data": {
                    # Overall coverage percentage (if available)
                    "coverage_percent": float,
                    # Path to the output file (for non-text formats)
                    "output_file": str
                }
            },
            # Error message if success is False, otherwise None
            "error": str | None
        }
    """
    return await TarpaulinTool(ctx, cwd, dict(args=tarpaulin_args)).run()
