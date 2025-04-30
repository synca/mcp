"""Isolated tests for synca.mcp.cargo.tool.tarpaulin."""

from unittest.mock import MagicMock

import pytest

from synca.mcp.cargo.tool.base import Tool, CargoTool
from synca.mcp.cargo.tool.tarpaulin import TarpaulinTool


def test_tool_tarpaulin_constructor():
    """Test TarpaulinTool class initialization."""
    ctx = MagicMock()
    path = MagicMock()
    tool = TarpaulinTool(ctx, path)
    assert isinstance(tool, TarpaulinTool)
    assert isinstance(tool, CargoTool)
    assert isinstance(tool, Tool)
    assert tool.ctx == ctx
    assert tool._path_str == path
    assert tool.tool_name == "tarpaulin"
    assert "tool_name" not in tool.__dict__


@pytest.mark.parametrize(
    "stdout",
    ["",
     "Running tests\n100.00% coverage",
     "Running tests\n75.50% coverage, warnings found"])
@pytest.mark.parametrize(
    "stderr",
    ["",
     "warning: unused variable",
     "error: compilation failed"])
@pytest.mark.parametrize(
    "has_notes",
    [False, True])
@pytest.mark.parametrize("return_code", [0, 1, None])
def test_tool_tarpaulin_parse_output(
        patches, stdout, stderr, has_notes, return_code):
    """Test TarpaulinTool.parse_output method with various inputs."""
    ctx = MagicMock()
    path = MagicMock()
    tool = TarpaulinTool(ctx, path)
    combined_output = stdout + "\n" + stderr
    mock_warnings = (
        ["warning: unused variable"]
        if "warning"
        in stderr
        else [])
    mock_errors = (
        ["error: compilation failed"]
        if "error"
        in stderr
        else [])
    mock_notes = ["note: consider using const"] if has_notes else []
    warnings_count = len(mock_warnings)
    errors_count = len(mock_errors)
    issues_count = warnings_count + errors_count
    coverage_percentage = (
        100.0
        if "100"
        in stdout
        else (75.5
              if "75"
              in stdout
              else 0.0))
    # Updated coverage structure to match new format
    mock_coverage = {
        "total": coverage_percentage,
        "by_file": {}
    }
    if coverage_percentage > 0:
        mock_coverage["output_file"] = "coverage.xml"
    expected_info = {}
    if warnings_count:
        expected_info["warnings_count"] = warnings_count
        expected_info["warnings"] = mock_warnings
    if errors_count:
        expected_info["errors_count"] = errors_count
        expected_info["errors"] = mock_errors
    if mock_notes:
        expected_info["notes"] = mock_notes
    expected_info["coverage"] = mock_coverage
    all_good = return_code == 0 and issues_count == 0
    expected_message = (
        f"Coverage: {coverage_percentage:.2f}%"
        if all_good
        else combined_output)
    expected_result = (
        return_code,
        issues_count,
        expected_message,
        expected_info)
    patched = patches(
        "TarpaulinTool.parse_issues",
        "TarpaulinTool._extract_coverage",
        prefix="synca.mcp.cargo.tool.tarpaulin")

    with patched as (m_parse_issues, m_extract_coverage):
        m_parse_issues.return_value = (mock_warnings, mock_errors, mock_notes)
        m_extract_coverage.return_value = mock_coverage
        assert (
            tool.parse_output(stdout, stderr, return_code)
            == expected_result)

    assert (
        m_parse_issues.call_args
        == [(combined_output,), {}])
    assert (
        m_extract_coverage.call_args
        == [(combined_output,), {}])


@pytest.mark.parametrize(
    "additional_error_matches",
    [True, False])
def test_tool_tarpaulin_parse_issues(patches, additional_error_matches):
    """Test TarpaulinTool.parse_issues method."""
    ctx = MagicMock()
    path = MagicMock()
    tool = TarpaulinTool(ctx, path)
    output = "output content"
    additional_errors = [
        "failed to execute",
        "couldn't find binary",
        "failed to parse",
        "error running tarpaulin"
    ]
    expected_return = (MagicMock(), MagicMock(), MagicMock())
    patched = patches(
        "CargoTool.parse_issues",
        prefix="synca.mcp.cargo.tool.base")

    with patched as (m_parse_issues,):
        m_parse_issues.return_value = expected_return
        assert (
            expected_return
            == tool.parse_issues(output))

    # Check that parent method was called with correct parameters
    assert (
        m_parse_issues.call_args
        == [(output, additional_errors), {}])


@pytest.mark.parametrize(
    "percent_value",
    ["100.00",
     "75.5",
     "0",
     "invalid",
     ""])
@pytest.mark.parametrize(
    "error",
    [None,
     ValueError,
     IndexError,
     BaseException])
def test_tool_tarpaulin_extract_coverage_percentage(
        patches, percent_value, error):
    """Test TarpaulinTool._extract_coverage_percentage with various
    inputs and errors.
    """
    ctx = MagicMock()
    path = MagicMock()
    tool = TarpaulinTool(ctx, path)
    line = MagicMock()
    if percent_value == "":
        line.split.return_value = []
    else:
        line.split.return_value = [percent_value]
    expected = (
        float(percent_value)
        if (error is None
            and percent_value != ""
            and percent_value != "invalid")
        else 0.0)
    patched = patches(
        "float",
        prefix="builtins")

    with patched as (m_float,):
        if error:
            m_float.side_effect = error("Test error")
        else:
            m_float.return_value = expected

        if error is BaseException and percent_value:
            with pytest.raises(BaseException):
                tool._extract_coverage_percentage(line)
        else:
            assert (
                tool._extract_coverage_percentage(line)
                == expected)

    assert (
        line.split.call_args
        == [("%",), {}])

    # Float will be called for non-empty strings except in empty string case
    if percent_value and percent_value != "":
        # For BaseException it's called before raising exception
        assert m_float.called
        # For all other cases verify the call arguments
        if error is not BaseException:
            assert (
                m_float.call_args
                == [(percent_value,), {}])
    else:
        # For empty string, float should not be called
        assert not m_float.called


@pytest.mark.parametrize(
    "output,expected",
    [("",
      {"coverage_percent": 0.0, "output_file": None}),
     ("Running tarpaulin...\n"
      "85.7% coverage, 10/12 lines covered\n"
      "No output file specified",
      {"coverage_percent": 85.7, "output_file": None}),
     ("Running tarpaulin...\n"
      "100.0% coverage, all lines covered\n"
      "Coverage Results: /path/to/coverage.xml",
      {"coverage_percent": 100.0, "output_file": "/path/to/coverage.xml"}),
     ("Running tarpaulin...\n"
      "75.5% coverage\n"
      "Writing coverage to: /path/to/coverage.html",
      {"coverage_percent": 75.5, "output_file": "/path/to/coverage.html"}),
     ("Running tarpaulin...\n"
      "Invalid% coverage\n"
      "No results",
      {"coverage_percent": 0.0, "output_file": None}),
     ("Running tarpaulin...\n"
      "50.0% coverage in module A\n"
      "75.0% coverage in module B\n"
      "Overall: 60.5% coverage\n"
      "Coverage Results: /path/to/coverage.json",
      {"coverage_percent": 60.5, "output_file": "/path/to/coverage.json"})])
def test_tool_tarpaulin_extract_coverage(patches, output, expected):
    """Test _extract_coverage method with various inputs."""
    ctx = MagicMock()
    path = MagicMock()
    tool = TarpaulinTool(ctx, path)

    # Setup mock side effects
    def mock_percentage(line):
        if "Overall:" in line and "%" in line:
            # For lines with "Overall:" prefix, extract that percentage
            parts = line.split("Overall:")[1].strip()
            is_percentage = (
                "%" in parts
                and parts.split("%")[0].strip().replace(".", "", 1).isdigit())
            return (
                float(parts.split("%")[0].strip())
                if is_percentage
                else None)
        is_percentage = (
            "%" in line
            and line.split("%")[0].strip().replace(".", "", 1).isdigit())
        return (
            float(line.split("%")[0].strip())
            if is_percentage
            else None)

    def mock_file(line):
        if "Writing coverage to:" in line:
            # Special case for "Writing coverage to:" format
            return line.split("to:")[1].strip()
        elif ":" in line:
            return line.split(":", 1)[1].strip()
        return None

    # Updated expected dictionary to match the new format
    updated_expected = {
        "total": expected.get("coverage_percent", 0.0),
        "by_file": {}
    }
    if expected.get("output_file"):
        updated_expected["output_file"] = expected["output_file"]

    # For the "Invalid%" test case, we need to handle None value
    if "Invalid%" in output:
        updated_expected["total"] = None

    patched = patches(
        "TarpaulinTool._extract_coverage_percentage",
        "TarpaulinTool._extract_output_file",
        prefix="synca.mcp.cargo.tool.tarpaulin")

    with patched as (m_extract_percentage, m_extract_file):
        m_extract_percentage.side_effect = mock_percentage
        m_extract_file.side_effect = mock_file

        assert (
            tool._extract_coverage(output)
            == updated_expected)

    # Verify extract_percentage calls
    expected_percentage_calls = []
    for line in output.splitlines():
        if "% coverage" in line:
            expected_percentage_calls.append(((line,), {}))

    assert (
        m_extract_percentage.call_args_list
        == expected_percentage_calls)

    # Verify extract_file calls
    expected_file_calls = []
    for line in output.splitlines():
        if "Coverage Results:" in line or "Writing coverage" in line:
            expected_file_calls.append(((line,), {}))

    assert (
        m_extract_file.call_args_list
        == expected_file_calls)


@pytest.mark.parametrize(
    "line,expected",
    [("",
      None),
     ("No output file specified",
      None),
     ("Coverage Results:",
      None),
     ("Coverage Results: /path/to/coverage.xml",
      "/path/to/coverage.xml"),
     ("Coverage Results: /path/to/coverage.json",
      "/path/to/coverage.json"),
     ("Writing coverage to: /path/to/coverage.html",
      "/path/to/coverage.html"),
     ("Writing coverage",
      None),
     ("Writing coverage: /tmp/tarpaulin/coverage.cobertura.xml",
      "/tmp/tarpaulin/coverage.cobertura.xml"),
     # Test with extra spaces
     ("Coverage Results:    /path/with spaces/coverage.xml  ",
      "/path/with spaces/coverage.xml")])
@pytest.mark.parametrize(
    "error",
    [None,
     ValueError,
     IndexError,
     BaseException])
def test_tool_tarpaulin_extract_output_file(patches, line, expected, error):
    """Test _extract_output_file method with various inputs and errors."""
    ctx = MagicMock()
    path = MagicMock()
    tool = TarpaulinTool(ctx, path)
    line_mock = MagicMock()

    # Empty split result will cause IndexError
    if error is None:
        result = tool._extract_output_file(line)
        if expected is None:
            assert result == ""
        else:
            assert result == expected
        return

    # Set up mock for error cases
    line_mock.split.side_effect = error("Test error")

    # BaseException should be propagated, not caught
    if error is BaseException:
        with pytest.raises(BaseException):
            tool._extract_output_file(line_mock)
    else:
        # Other exceptions should return empty string now, not None
        result = tool._extract_output_file(line_mock)
        assert result == ""

    # Verify the call was made correctly in all error cases
    assert (
        line_mock.split.call_args
        == [(':', 1), {}])
