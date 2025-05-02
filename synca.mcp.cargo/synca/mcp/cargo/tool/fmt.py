"""Tool for running cargo fmt."""

from synca.mcp.cargo.tool.base import CargoTool
from synca.mcp.common.types import OutputTuple, OutputInfoDict


class FmtTool(CargoTool):
    """Tool for running cargo fmt on a Rust project."""

    @property
    def tool_name(self) -> str:
        """Return the name of the tool."""
        return "fmt"

    def parse_output(
            self,
            stdout: str,
            stderr: str,
            return_code: int) -> OutputTuple:
        """Parse the cargo fmt output.

        Args:
            stdout: Standard output from the command
            stderr: Standard error from the command
            return_code: Return code from the command

        Returns:
            Tuple containing:
            - Return code
            - Number of issues found (0 or 1 for fmt)
            - Output message
            - Additional information dictionary
        """
        combined_output = stdout + "\n" + stderr
        info: OutputInfoDict = {}
        warnings, errors, notes = self.parse_issues(combined_output)
        if warnings:
            info["warnings_count"] = len(warnings)
            info["warnings"] = warnings
        if errors:
            info["errors_count"] = len(errors)
            info["errors"] = errors
        if notes:
            info["notes"] = notes
        needs_formatting = (
            "Diff in" in combined_output
            and return_code != 0)
        info["needs_formatting"] = needs_formatting
        message = (
            "Code is properly formatted"
            if return_code == 0
            else "Cargo fmt failed")
        return (
            return_code or 0,
            message,
            combined_output.strip(),
            info)
