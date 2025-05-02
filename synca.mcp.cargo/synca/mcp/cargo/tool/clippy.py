"""Tool for running cargo clippy."""

from synca.mcp.cargo.tool.base import CargoTool
from synca.mcp.common.types import IssuesTuple, OutputInfoDict, OutputTuple


class ClippyTool(CargoTool):
    """Tool for running cargo clippy on a Rust project."""

    @property
    def tool_name(self) -> str:
        """Return the name of the tool."""
        return "clippy"

    def parse_output(
            self,
            stdout: str,
            stderr: str,
            return_code: int | None) -> OutputTuple:
        """Parse the clippy output."""
        # Combine stdout and stderr for analysis
        combined_output = stdout + "\n" + stderr
        info: OutputInfoDict = {}
        warnings, errors, resolutions = self.parse_issues(combined_output)
        if warnings:
            info["warnings_count"] = len(warnings)
            if warnings:
                info["warning_types"] = self._categorize_issues(
                    warnings, "warning")
        if errors:
            info["errors_count"] = len(errors)
            if errors:
                info["error_types"] = self._categorize_issues(
                    errors, "error")
        if resolutions:
            info["resolutions"] = resolutions
        issues_count = len(warnings) + len(errors)
        all_good = (
            issues_count == 0
            and return_code == 0
            and "Finished" in combined_output)
        return (
            return_code or 0,
            ("No issues found"
             if all_good
             else f"Issues found: {issues_count}"),
            (""
             if all_good
             else combined_output),
            info)

    def _categorize_issues(
            self,
            issues: list[str],
            issue_type: str) -> dict[str, int]:
        """Categorize clippy warnings or errors by their type."""
        categories: dict[str, int] = {}
        for issue in issues:
            parts = issue.split(f"{issue_type}: ", 1)
            if len(parts) <= 1:
                continue
            category_part = parts[1]
            category = (
                category_part.split(":", 1)[0]
                if ":" in category_part
                else category_part)
            categories[category] = categories.get(category, 0) + 1
        return categories

    def parse_issues(
            self,
            combined_output: str,
            additional_errors: list[str] | None = None) -> IssuesTuple:
        """Parse warnings, errors, and resolutions from clippy output."""
        warnings, errors, resolutions = [], [], []
        for line in combined_output.splitlines():
            if "cargo clippy --fix" in line:
                resolutions.append(line)
            elif "error:" in line:
                errors.append(line)
            elif "warning:" in line:
                warnings.append(line)

        return warnings, errors, resolutions
