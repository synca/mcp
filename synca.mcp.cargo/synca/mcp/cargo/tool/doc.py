"""Tool for running cargo doc."""

from synca.mcp.cargo.tool.base import CargoTool
from synca.mcp.common.types import OutputInfoDict, OutputTuple


class DocTool(CargoTool):
    """Tool for generating documentation for Rust projects."""

    @property
    def tool_name(self) -> str:
        """Return the name of the tool."""
        return "doc"

    def parse_output(
            self,
            stdout: str,
            stderr: str,
            return_code: int) -> OutputTuple:
        """Parse the cargo doc output.

        Args:
            stdout: Standard output from the command
            stderr: Standard error from the command
            return_code: Return code from the command

        Returns:
            Tuple containing:
            - Return code
            - Number of issues found (always 0 for doc)
            - Output message
            - Additional information dictionary
        """
        combined_output = stdout + "\n" + stderr
        info: OutputInfoDict = {}
        target_doc_path = self.path / "target" / "doc"
        if package_name := self._extract_package_name():
            info["artifact_path"] = str(target_doc_path / package_name)
        warnings, errors, notes = self.parse_issues(combined_output)
        if warnings:
            info["warnings_count"] = len(warnings)
            info["warnings"] = warnings
        if errors:
            info["errors_count"] = len(errors)
            info["errors"] = errors
        if notes:
            info["notes"] = notes
        issues_count = len(warnings) + len(errors)
        all_good = (
            issues_count == 0
            and return_code == 0
            and "Finished" in combined_output)
        return (
            return_code or 0,
            ("Documentation successfully generated"
             if all_good
             else "Documentation generation failed"),
            (""
             if all_good
             else combined_output),
            info)

    def _extract_package_name(self) -> str | None:
        """Extract the package name from Cargo.toml.

        Returns:
            The package name if found, None otherwise
        """
        cargo_toml_path = self.path / "Cargo.toml"
        for line in cargo_toml_path.read_text().splitlines():
            if line.strip().startswith("name") and "=" in line:
                package_name = line.split("=")[1].strip().strip('"').strip("'")
                return package_name
        return None
