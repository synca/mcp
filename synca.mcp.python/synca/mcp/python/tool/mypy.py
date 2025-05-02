"""Mypy type checker tool implementation for MCP server."""

from synca.mcp.python.tool.base import PythonTool


class MypyTool(PythonTool):
    """Mypy type checker tool implementation."""

    @property
    def tool_name(self) -> str:
        return "mypy"

    def parse_issues(self, stdout: str, stderr: str) -> int:
        stdout_length = len(stdout.strip().splitlines())
        return (
            (stdout_length - 1)
            if stdout.strip()
            else 0)
