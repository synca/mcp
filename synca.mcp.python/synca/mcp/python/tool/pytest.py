"""Pytest runner tool implementation for MCP server."""

import re

from synca.mcp.common.tool import Tool
from synca.mcp.common.types import OutputInfoDict, OutputTuple
from synca.mcp.python.util.coverage import CoverageParser


class PytestTool(Tool):
    """Pytest runner tool implementation."""

    @property
    def tool_name(self):
        return "pytest"

    def parse_output(
            self,
            stdout: str,
            stderr: str,
            returncode: int | None) -> OutputTuple:
        """Parse the tool output."""
        combined_output = stdout + "\n" + stderr
        data: OutputInfoDict = dict(
            summary=self._parse_summary(combined_output),
            coverage=(
                self._parse_coverage(combined_output)
                or dict(total=0.0, by_file={})))
        issues_count = data["summary"]["failed"]
        if data["coverage"].get("failure"):
            issues_count += 1
        message = (
            "All tests passed successfully"
            if returncode == 0
            else combined_output)
        return returncode or 0, issues_count, message, data

    def _parse_coverage(
            self,
            output: str
    ) -> dict[str, float | dict[str, float]] | None:
        """Extract coverage statistics from pytest output.
        """
        if "Required test coverage" not in output:
            return None
        return CoverageParser(output).data

    def _parse_summary(
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
