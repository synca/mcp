"""Tool for running cargo tarpaulin."""

from synca.mcp.cargo.tool.base import CargoTool
from synca.mcp.common.types import (
    CoverageDict, IssuesTuple, OutputTuple, OutputInfoDict)


class TarpaulinTool(CargoTool):
    """Tool for running cargo tarpaulin on a Rust project."""

    @property
    def tool_name(self) -> str:
        """Return the name of the tool."""
        return "tarpaulin"

    def parse_output(
            self,
            stdout: str,
            stderr: str,
            return_code: int) -> OutputTuple:
        """Parse tarpaulin output.

        Extracts coverage data, warnings, and errors from tarpaulin output.
        """
        combined_output = stdout + "\n" + stderr
        info: OutputInfoDict = {}
        warnings, errors, notes = self.parse_issues(combined_output)
        warnings_count = 0
        errors_count = 0
        if warnings:
            warnings_count = len(warnings)
            info["warnings_count"] = warnings_count
            info["warnings"] = warnings
        if errors:
            errors_count = len(errors)
            info["errors_count"] = errors_count
            info["errors"] = errors
        if notes:
            info["notes"] = notes
        coverage = self._extract_coverage(combined_output)
        info["coverage"] = coverage
        issues_count = warnings_count + errors_count
        all_good = return_code == 0 and issues_count == 0
        message = (
            f"Coverage: {coverage.get('total', 0):.2f}%"
            if all_good
            else "Issues found during coverage analysis")
        return (
            return_code,
            message,
            "" if all_good else combined_output,
            info)

    def parse_issues(
            self,
            combined_output: str,
            additional_errors: list[str] | None = None) -> IssuesTuple:
        """Parse warnings, errors and notes from tarpaulin output."""
        if additional_errors is None:
            additional_errors = [
                "failed to execute",
                "couldn't find binary",
                "failed to parse",
                "error running tarpaulin"
            ]
        return super().parse_issues(combined_output, additional_errors)

    def _extract_coverage(
            self,
            output: str) -> CoverageDict:
        """Extract coverage data from tarpaulin output."""
        coverage_percent = 0.0
        output_file = None

        write_lines = ["Coverage Results:", "Writing coverage"]
        for line in output.splitlines():
            if "% coverage" in line:
                coverage_percent = self._extract_coverage_percentage(line)
            elif any(x in line for x in write_lines):
                output_file = self._extract_output_file(line)

        # Create a valid CoverageDict structure
        coverage: CoverageDict = {
            "total": coverage_percent,
            "by_file": {}
        }

        # Add optional fields if available
        if output_file and output_file != "":
            coverage["output_file"] = output_file

        return coverage

    def _extract_coverage_percentage(self, line: str) -> float:
        """Extract coverage percentage from a line."""
        try:
            percent_str = line.split("%")[0].strip()
            return float(percent_str)
        except (ValueError, IndexError):
            return 0.0

    def _extract_output_file(self, line: str) -> str:
        """Extract output file path from a line."""
        try:
            parts = line.split(":", 1)
            if len(parts) > 1:
                if path := parts[1].strip():
                    return path
            return ""
        except (IndexError, ValueError):
            return ""
