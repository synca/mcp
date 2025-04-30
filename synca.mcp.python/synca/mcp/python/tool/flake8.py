"""Flake8 linter tool implementation for MCP server."""

from synca.mcp.common.tool import Tool
from synca.mcp.common.types import OutputTuple


class Flake8Tool(Tool):
    """Flake8 linter tool implementation."""

    @property
    def tool_name(self) -> str:
        return "flake8"

    def parse_output(
            self,
            stdout: str,
            stderr: str,
            returncode: int | None) -> OutputTuple:
        """Parse the tool output."""
        if (returncode or 0) > 1:
            raise RuntimeError(f"{self.tool_name} failed: {stderr}")
        combined_output = stdout + "\n" + stderr
        stdout_length = len(stdout.strip().splitlines())
        issues_count = stdout_length if stdout.strip() else 0
        strip_out = combined_output.strip()
        msg_output = strip_out if strip_out else "No issues found"
        return returncode or 0, issues_count, msg_output, {}
