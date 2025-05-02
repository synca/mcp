"""Tool for running cargo build."""

from synca.mcp.cargo.tool.base import CargoTool
from synca.mcp.common.types import (
    OutputInfoDict, OutputTuple, TimingInfoDict, StatusDict)


class BuildTool(CargoTool):
    """Tool for building Rust projects."""

    @property
    def tool_name(self) -> str:
        """Return the name of the tool."""
        return "build"

    def parse_output(
            self,
            stdout: str,
            stderr: str,
            return_code: int) -> OutputTuple:
        """Parse the build output."""
        combined_output = stdout + "\n" + stderr
        info: OutputInfoDict = {}
        warnings, errors, notes = self.parse_issues(combined_output)
        if mode := self._extract_mode(combined_output):
            info["mode"] = mode
        if timing := self._extract_timing(combined_output):
            info["timing"] = timing
        if statuses := self._extract_target_statuses(combined_output):
            info["statuses"] = statuses
        if warnings:
            info["warnings_count"] = len(warnings)
            info["warnings"] = warnings
        if errors:
            info["errors_count"] = len(errors)
            info["errors"] = errors
        if notes:
            info["notes"] = notes
        issues_count = len(warnings) + len(errors)
        successful = return_code == 0 and "Finished" in combined_output
        return (
            return_code,
            ("Build completed successfully with no issues"
             if (successful
                 and not issues_count)
             else f"Build issues: {issues_count}"),
            (""
             if (successful
                 and not issues_count)
             else combined_output),
            info)

    def _extract_mode(self, combined_output: str) -> str | None:
        """Extract the build mode (debug/release) from output."""
        for line in combined_output.splitlines():
            if "Finished dev" in line or "Finished test" in line:
                return "debug"
            elif "Finished release" in line:
                return "release"
        return None

    def _extract_timing(self, combined_output: str) -> TimingInfoDict:
        """Extract build timing information if available."""
        timing_info: TimingInfoDict = dict(total="")
        for line in combined_output.splitlines():
            if "Finished" in line and "in" in line:
                if status := self._status_finished(line):
                    timing_info["total"] = status
                    return timing_info
        return None if not timing_info else timing_info

    def _status_finished(self, line: str) -> str | None:
        """Extract timing information from a 'Finished' line."""
        try:
            time_part = line.split("in ")[-1].strip()
            if time_part.endswith("s"):
                return time_part
        except (IndexError, ValueError):
            pass
        return None

    def _extract_target_statuses(
            self,
            combined_output: str) -> dict[str, StatusDict] | None:
        """Extract compilation status of individual targets."""
        statuses: dict[str, StatusDict] = {}
        for line in combined_output.splitlines():
            if line.startswith("Compiling "):
                if status := self._status_compiling(line):
                    statuses[status[0]] = status[1]
            elif line.startswith("Fresh "):
                if status := self._status_fresh(line):
                    statuses[status[0]] = status[1]
        return None if not statuses else statuses

    def _status_compiling(
            self,
            line: str) -> tuple[str, StatusDict] | None:
        """Extract compiling status for a target."""
        try:
            parts = line.split("Compiling ")[1].strip().split(" ")
            if len(parts) >= 1:
                status_dict: StatusDict = {"status": "compiling"}
                if len(parts) > 1:
                    status_dict["version"] = parts[1]
                return parts[0], status_dict
        except (IndexError, ValueError):
            pass
        return None

    def _status_fresh(
            self,
            line: str) -> tuple[str, StatusDict] | None:
        """Extract fresh status for a target."""
        try:
            parts = line.split("Fresh ")[1].strip().split(" ")
            if len(parts) >= 1:
                status_dict: StatusDict = {"status": "fresh"}
                if len(parts) > 1:
                    status_dict["version"] = parts[1]
                return parts[0], status_dict
        except (IndexError, ValueError):
            pass
        return None
