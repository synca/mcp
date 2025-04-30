"""Tool for running cargo run."""

from synca.mcp.cargo.tool.base import CargoTool
from synca.mcp.common.types import OutputTuple, OutputInfoDict


class RunTool(CargoTool):
    """Tool for running cargo run on a Rust project."""

    @property
    def tool_name(self) -> str:
        """Return the name of the tool."""
        return "run"

    def parse_output(
            self,
            stdout: str,
            stderr: str,
            return_code: int | None) -> OutputTuple:
        """Parse the cargo run output.
        """
        combined_output = stdout + "\n" + stderr
        info: OutputInfoDict = {}
        warnings, errors, notes = self.parse_issues(combined_output)
        build_mode, binary_name, compilation_output, program_output = (
            self._extract_all(combined_output))
        info["mode"] = build_mode or "debug"
        if binary_name:
            info["artifact_path"] = binary_name
        if compilation_output:
            info["compilation_output"] = compilation_output
        if program_output:
            info["program_output"] = program_output
        if warnings:
            info["warnings_count"] = len(warnings)
            info["warnings"] = warnings
        if errors:
            info["errors_count"] = len(errors)
            info["errors"] = errors
        if notes:
            info["notes"] = notes
        if errors:
            # Use error_types instead of error_type for mypy compatibility
            error_type = self._determine_error_type(errors)
            info["error_types"] = {error_type: 1}
        issues_count = len(warnings) + len(errors)
        successful = return_code == 0 and not issues_count
        message = (
            "Program executed successfully"
            if successful
            else ("Failed to compile the program"
                  if (next(iter(info.get("error_types", {})), "")
                      == "compilation")
                  else "Program execution failed"))
        output = message if successful else combined_output
        return (return_code or 0, issues_count, output, info)

    def _extract_all(
            self,
            combined_output: str) -> tuple[
                str | None, str | None, str | None, str]:
        """Extract all metadata in a single pass through the output.
        """
        lines = combined_output.splitlines()
        build_mode = None
        binary_name = None
        running_line_idx = None

        # Single pass to collect all metadata
        for i, line in enumerate(lines):
            if not build_mode:
                build_mode = self._extract_build_mode_from_line(line)
            if not running_line_idx and "Running `" in line:
                running_line_idx = i
                if not binary_name:
                    binary_name = self._extract_binary_name_from_line(line)

        # Process outputs based on running line index
        compilation_output, program_output = (
            self._split_outputs(lines, running_line_idx, combined_output))

        return build_mode, binary_name, compilation_output, program_output

    def _extract_build_mode_from_line(self, line: str) -> str | None:
        """Extract build mode from a single line."""
        if "Finished dev" in line or "Finished test" in line:
            return "debug"
        elif "Finished release" in line:
            return "release"
        return None

    def _extract_binary_name_from_line(self, line: str) -> str | None:
        """Extract binary name from a single line."""
        if "Running `" in line and "target" in line:
            try:
                parts = line.split('`')[1].split()[0].split('/')
                return parts[-1]  # Last part should be binary name
            except (IndexError, ValueError):
                pass
        return None

    def _split_outputs(
            self,
            lines: list[str],
            running_line_idx: int | None,
            combined_output: str) -> tuple[str | None, str]:
        """Split the output into compilation and program parts."""
        if running_line_idx is None:
            return None, combined_output
        compilation_output = "\n".join(lines[:running_line_idx+1])
        program_output = "\n".join(lines[running_line_idx+1:])
        return (
            (compilation_output
             if compilation_output.strip()
             else None),
            (program_output
             if program_output.strip()
             else combined_output))

    def _determine_error_type(self, errors: list[str]) -> str:
        """Determine if errors are compilation errors or runtime errors."""
        for error in errors:
            if "could not compile" in error.lower():
                return "compilation"
        return "runtime"
