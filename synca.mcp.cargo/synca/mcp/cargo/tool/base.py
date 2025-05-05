"""Base Tool class for MCP server tools."""

import pathlib

from synca.mcp.common.tool import CLICheckTool
from synca.mcp.common.types import CommandTuple, IssuesTuple


class CargoTool(CLICheckTool):
    """Base class for Cargo tools."""

    @property
    def command(self) -> CommandTuple:
        """Build the command with cargo prefix."""
        return (
            "cargo",
            self.tool_name,
            *self.args)

    @property
    def tool_path(self) -> str:
        """Return the tool name without cargo prefix."""
        return self.tool_name

    def parse_issues(
            self,
            combined_output: str,
            additional_errors: list[str] | None = None) -> IssuesTuple:
        """Extract warnings, errors, and notes from the build output.
        """
        warnings, errors, notes = [], [], []
        for line in combined_output.splitlines():
            line = line.strip()
            if not line:
                continue
            has_additional_error = (
                additional_errors
                and any(
                    err in line.lower()
                    for err in additional_errors))
            if has_additional_error:
                errors.append(line)
            # Then standard error/warning/note patterns
            elif "error:" in line.lower():
                errors.append(line)
            elif "warning:" in line.lower():
                warnings.append(line)
            elif "note:" in line.lower():
                notes.append(line)
        return warnings, errors, notes

    def validate_path(self, path: pathlib.Path) -> None:
        """Validate that the project path contains a Cargo.toml file."""
        super().validate_path(path)
        cargo_toml_path = path / "Cargo.toml"
        if not cargo_toml_path.exists():
            raise FileNotFoundError(
                f"Path '{path}' is not a valid Rust project "
                "(no Cargo.toml found)")
