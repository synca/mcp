"""Tool for running cargo test."""

from synca.mcp.cargo.tool.base import CargoTool
from synca.mcp.common.types import OutputTuple, OutputInfoDict


class TestTool(CargoTool):
    """Tool for running cargo test on a Rust project."""

    @property
    def tool_name(self) -> str:
        """Return the name of the tool."""
        return "test"

    def parse_output(
            self,
            stdout: str,
            stderr: str,
            return_code: int) -> OutputTuple:
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
        summary = info["summary"] = self._extract_summary(combined_output)
        test_failures = (
            int(summary.get("failed", 0))
            if summary
            else 0)
        issues_count = test_failures + errors_count + warnings_count
        all_good = return_code == 0 and issues_count == 0
        message = (
            "All tests passed successfully"
            if all_good
            else "Some tests failed")
        return (
            return_code,
            message,
            "" if all_good else combined_output,
            info)

    def _extract_summary(
            self,
            combined_output: str) -> dict[str, int | str]:
        summary: dict[str, int | str] = {}
        summary["status"] = "unknown"
        for line in combined_output.splitlines():
            if "test result: ok." in line:
                if result := self._parse_success_result(line):
                    summary.update(result)
                    break
            elif "test result: FAILED" in line:
                if result := self._parse_failure_result(line):
                    summary.update(result)
                    break
        return summary

    def _parse_success_result(self, line: str) -> dict[str, int | str] | None:
        try:
            parts = line.split()
            test_count = int(parts[3])
            return {
                "total_tests": test_count,
                "passed": test_count,
                "failed": 0,
                "status": "passed"
            }
        except (IndexError, ValueError):
            return None

    def _parse_failure_result(self, line: str) -> dict[str, int | str] | None:
        try:
            parts = line.split()
            failed_idx = parts.index("failed;") - 1
            passed_idx = (parts.index("passed;") or 1) - 1
            fail_count = int(parts[failed_idx])
            pass_count = int(parts[passed_idx])
            return {
                "total_tests": fail_count + pass_count,
                "passed": pass_count,
                "failed": fail_count,
                "status": "failed"
            }
        except (IndexError, ValueError):
            return None
