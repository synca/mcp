"""Mypy type checker tool implementation for MCP server."""

from snake.mcp.server.tools.base import Tool


class MypyTool(Tool):
    """Mypy type checker tool implementation."""

    @property
    def tool_name(self) -> str:
        return "mypy"

    def parse_output(
            self,
            stdout: str,
            stderr: str,
            returncode: int | None) -> tuple[int, str, dict]:
        """Parse the tool output.
        """
        if (returncode or 0) > 1:
            raise RuntimeError(f"{self.tool_name} failed: {stderr}")
        combined_output = stdout + "\n" + stderr
        stdout_length = len(stdout.strip().splitlines())
        issues_count = (stdout_length - 1) if stdout.strip() else 0
        strip_out = combined_output.strip()
        msg_output = strip_out if issues_count else "No issues found"
        return issues_count, msg_output, {}
