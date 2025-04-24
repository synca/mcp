"""Coverage parsing and handling for pytest tool."""

from typing import Any, Optional


class CoverageParsingError(Exception):
    """Raised when coverage parsing fails in a specific way."""
    pass


def parse_coverage_data(combined_output: str) -> dict[str, Any]:
    """Parse coverage information from pytest output.

    Args:
        combined_output: The combined stdout and stderr output from pytest

    Returns:
        A dictionary with coverage data:
        {
            "total": float,  # Total coverage percentage
            "by_file": dict  # Coverage by file
        }
    """
    coverage_data: dict[str, Any] = {
        "total": 0.0,
        "by_file": {}
    }
    # Look for the coverage table format:
    # Name                           Stmts   Miss  Cover
    # --------------------------------------------------
    # snake/__init__.py                  0      0   100%
    # TOTAL                            444     49    89%
    # Parse the coverage table from the output
    table_lines = _extract_coverage_table(combined_output)
    if not table_lines:
        return coverage_data  # Return empty data if no table found
    # Process each line of the coverage table
    for line in table_lines:
        if not line.strip():
            continue
        parts = line.split()
        if len(parts) < 4:
            continue
        file_path, cov_value = _extract_coverage_entry(parts)
        if file_path is not None and cov_value is not None:
            # Check if this is the TOTAL line
            if file_path == "TOTAL":
                coverage_data["total"] = cov_value
            else:
                coverage_data["by_file"][file_path] = cov_value
    return coverage_data


def _extract_coverage_table(output: str) -> list[str]:
    """Extract the coverage table lines from pytest output.

    Args:
        output: The combined stdout and stderr output from pytest

    Returns:
        List of lines from the coverage table
    """
    lines = output.splitlines()
    table_lines: list[str] = []
    in_coverage_table = False
    for line in lines:
        # Identify the start of coverage table
        if ("Name" in line and "Stmts" in line and "Miss" in line and
                "Cover" in line):
            in_coverage_table = True
            continue
        # Skip separator line
        if in_coverage_table and line.strip().startswith("--"):
            continue
        # End of table detection
        if in_coverage_table and ("TOTAL" in line or not line.strip()):
            if "TOTAL" in line:
                table_lines.append(line)  # Include the TOTAL line
            in_coverage_table = False
            continue
        # Add table content
        if in_coverage_table:
            table_lines.append(line)
    return table_lines


def _extract_coverage_entry(
        parts: list[str]) -> tuple[Optional[str], Optional[float]]:
    """Extract file path and coverage percentage from a table row.

    Args:
        parts: Split line from coverage table

    Returns:
        Tuple of file path and coverage percentage, or None if parsing fails
    """
    try:
        # The format is typically: name stmts miss cover
        # But name might have spaces, so we need to handle that
        if len(parts) < 4:
            return None, None
        # The last element should be the coverage percentage
        coverage_str = parts[-1]
        if not coverage_str.endswith('%'):
            return None, None
        # Extract the percentage value
        coverage_value = float(coverage_str.rstrip('%'))
        # The file path is everything except the last 3 elements
        file_parts = parts[:-3]
        file_path = ' '.join(file_parts)
        return file_path, coverage_value
    except (ValueError, IndexError):
        return None, None
