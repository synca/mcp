"""Pytest runner tool implementation for MCP server."""

import re

from snake.mcp.server.tools.base import Tool
from snake.mcp.server.util.coverage import CoverageParser


class PytestTool(Tool):
    """Pytest runner tool implementation."""

    @property
    def tool_name(self):
        return "pytest"

    def parse_output(
            self,
            stdout: str,
            stderr: str,
            returncode: int | None) -> tuple[int, str, dict]:
        """Parse the tool output."""
        combined_output = stdout + "\n" + stderr
        data: dict[str, dict] = dict(
            test_summary=self._parse_test_summary(combined_output),
            coverage=(
                self._parse_coverage_data(combined_output)
                or dict(total=0.0, by_file={})))
        issues_count = data["test_summary"]["failed"]
        if data["coverage"].get("failure"):
            issues_count += 1
        message = (
            "All tests passed successfully"
            if returncode == 0
            else combined_output)
        return issues_count, message, data

    def _parse_coverage_data(
            self,
            output: str
    ) -> dict[str, float | dict[str, float]] | None:
        """Extract coverage statistics from pytest output.
        """
        if "Required test coverage" not in output:
            return None
        return CoverageParser(output).data

    def _parse_test_summary(
            self,
            output: str
    ) -> dict[str, int]:
        """Extract test summary statistics from pytest output."""
        summary = {
            "total": 0,
            "passed": 0,
            "failed": 0,
            "skipped": 0,
            "xfailed": 0,
            "xpassed": 0
        }
        summary_match = re.search(
            r"=+ (.*?) in ([0-9.]+)s =+", output)
        if not summary_match:
            return summary
        summary_text = summary_match.group(1).strip()
        if summary_text == "no tests ran":
            return summary
        for state in ["passed", "failed", "skipped", "xfailed", "xpassed"]:
            match = re.search(rf"(\d+) {state}", summary_text)
            if match:
                summary[state] = int(match.group(1))
        total = sum(v for k, v in summary.items() if k != "total")
        summary["total"] = total
        return summary
