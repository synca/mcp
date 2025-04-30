"""Tool for running cargo check."""

from synca.mcp.cargo.tool.base import CargoTool
from synca.mcp.common.types import IssuesTuple, OutputInfoDict, OutputTuple


class CheckTool(CargoTool):
    """Tool for running cargo check on a Rust project."""

    @property
    def tool_name(self) -> str:
        """Return the name of the tool."""
        return "check"

    def parse_output(
            self,
            stdout: str,
            stderr: str,
            return_code: int | None) -> OutputTuple:
        """Parse the cargo check output.

        Args:
            stdout: Standard output from the command
            stderr: Standard error from the command
            return_code: Return code from the command

        Returns:
            Tuple containing:
            - Return code
            - Number of issues found
            - Output message
            - Additional information dictionary
        """
        # Combine stdout and stderr for analysis
        combined_output = stdout + "\n" + stderr
        info: OutputInfoDict = {}
        warnings, errors, resolutions = self.parse_issues(combined_output)
        if warnings:
            info["warnings_count"] = len(warnings)
            info["warning_messages"] = warnings
        if errors:
            info["errors_count"] = len(errors)
            info["errors"] = errors
        if resolutions:
            info["resolutions"] = resolutions
        issues_count = len(warnings) + len(errors)
        all_good = (
            issues_count == 0
            and return_code == 0
            and "Finished" in combined_output)
        return (
            return_code,
            issues_count,
            ("No issues found"
             if all_good
             else combined_output),
            info)

    def parse_issues(
            self,
            combined_output: str,
            additional_errors: list[str] | None = None) -> IssuesTuple:
        """Parse warnings, errors, and resolutions from cargo check output.

        Args:
            combined_output: Combined stdout and stderr
            additional_errors: Additional error patterns to look for

        Returns:
            Tuple containing:
            - List of warning messages
            - List of error messages
            - List of resolution suggestions
        """
        warnings = []
        errors = []
        resolutions = []
        for line in combined_output.splitlines():
            line = line.strip()
            if "cargo fix" in line:
                resolutions.append(line)
            elif "warning:" in line:
                warnings.append(line)
            elif "error:" in line:
                errors.append(line)

        return warnings, errors, resolutions
