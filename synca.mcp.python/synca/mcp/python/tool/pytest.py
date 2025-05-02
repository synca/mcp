"""Pytest runner tool implementation for MCP server."""

import re
from typing import cast

from synca.mcp.common.types import CoverageDict, OutputInfoDict, OutputTuple
from synca.mcp.python.tool.base import PythonTool
from synca.mcp.python.util.coverage import CoverageParser


class PytestTool(PythonTool):
    """Pytest runner tool implementation."""

    @property
    def tool_name(self):
        return "pytest"

    def parse_output(
            self,
            stdout: str,
            stderr: str,
            returncode: int) -> OutputTuple:
        """Parse the tool output."""
        combined_output = stdout + "\n" + stderr
        summary = self._parse_summary(combined_output)
        coverage = self._parse_coverage(combined_output)
        data: OutputInfoDict = dict(
            summary=cast(dict[str, str | int], summary))
        if coverage := self._parse_coverage(combined_output):
            data["coverage"] = coverage
        issues_count = int(summary["failed"])
        if coverage and coverage.get("failure"):
            issues_count += 1
        message = (
            "All tests passed successfully"
            if returncode == 0
            else f"Tests failed: {issues_count} issues found")
        return (
            returncode,
            message,
            (combined_output
             if issues_count
             else ""),
            data)

    def _parse_coverage(
            self,
            output: str
    ) -> CoverageDict | None:
        """Extract coverage statistics from pytest output.
        """
        if "Required test coverage" not in output:
            return None
        return cast(
            CoverageDict,
            CoverageParser(output).data
            or dict(total=0.0, by_file={}))

    def _parse_summary(
            self,
            output: str
    ) -> dict[str, int]:
        """Extract test summary statistics from pytest output."""
        summary: dict[str, int] = {
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
