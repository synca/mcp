"""Coverage parsing and handling for pytest tool."""

from functools import cached_property


class CoverageParsingError(Exception):
    """Raised when coverage parsing fails in a specific way."""
    pass


class CoverageParser:
    """Parser for coverage information from pytest output."""
    _in_coverage_table = False

    def __init__(self, combined_output: str) -> None:
        """Initialize with pytest output."""
        self.combined_output = combined_output

    @property
    def data(self) -> dict[str, float | dict[str, float]]:
        """Parse coverage information from pytest output."""
        # Look for the coverage table format:
        # Name                           Stmts   Miss  Cover
        # --------------------------------------------------
        # snake/__init__.py                  0      0   100%
        # TOTAL                            444     49    89%
        # Parse the coverage table from the output
        coverage_data: dict[str, float | dict[str, float]] = dict(
            total=0.0,
            by_file={})
        for row in self.table:
            self._parse_table_row(coverage_data, row)
        return coverage_data

    @cached_property
    def table(self) -> list[list[str]]:
        """Extract the coverage table lines from pytest output."""
        lines = self.combined_output.splitlines()
        table_rows: list[list[str]] = []
        for line in lines:
            if row := self._table_row(line):
                table_rows.append(row)
        return table_rows

    def _coverage_table_start(self, line) -> bool:
        return (
            "Name" in line
            and "Stmts" in line
            and "Miss" in line
            and "Cover" in line)

    def _parse_table_row(self, coverage_data, row) -> None:
        if not (result := self._table_entry(row)):
            return
        file_path, cov_value = result
        if file_path == "TOTAL":
            coverage_data["total"] = cov_value
        elif file_path.startswith("FAIL"):
            coverage_data["failure"] = file_path
        else:
            coverage_data["by_file"][file_path] = cov_value

    def _table_entry(
            self,
            row: list[str]) -> tuple[str, float] | None:
        """Extract file path and coverage percentage from a table row."""
        if len(row) < 4 or not row[-1].endswith('%'):
            return None
        try:
            coverage_value = float(row[-1].rstrip('%'))
        except ValueError:
            return None
        return " ".join(row[:-3]), coverage_value

    def _table_row(
            self,
            line: str) -> list[str] | None:
        if not self._in_coverage_table:
            if self._coverage_table_start(line):
                self._in_coverage_table = True
            return None
        if line.strip().startswith("--"):
            return None
        if "TOTAL" in line or not line.strip():
            if "TOTAL" in line:
                return line.split()
            self._in_coverage_table = False
            return None
        return line.split()
