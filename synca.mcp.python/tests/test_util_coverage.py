"""Isolated tests for synca.mcp.python.util.coverage."""

import pytest
from unittest.mock import MagicMock, PropertyMock

# Import the coverage module for testing
from synca.mcp.python.util import coverage


def test_coverage_parsing_error():
    """Test CoverageParsingError exception class."""
    error = coverage.CoverageParsingError("Test error message")
    assert isinstance(error, Exception)
    assert str(error) == "Test error message"


def test_coverage_parser_constructor():
    """Test CoverageParser class initialization."""
    combined_output = MagicMock()
    parser = coverage.CoverageParser(combined_output)
    assert isinstance(parser, coverage.CoverageParser)
    assert parser.combined_output == combined_output


def test_coverage_data(patches, iters):
    """Test data property with parametrized inputs including error cases."""
    combined_output = MagicMock()
    parser = coverage.CoverageParser(combined_output)
    table_rows = iters()
    patched = patches(
        "dict",
        ("CoverageParser.table",
         dict(new_callable=PropertyMock)),
        "CoverageParser._parse_table_row",
        prefix="synca.mcp.python.util.coverage")

    with patched as (m_dict, m_table, m_row):
        m_table.return_value = table_rows
        result = parser.data
        assert (
            result
            == m_dict.return_value)

    assert (
        m_row.call_args_list
        == [[(result, row), {}] for row in table_rows])

    assert (
        m_dict.call_args
        == [(), dict(total=0.0, by_file={})])


@pytest.mark.parametrize(
    "entry,expected_update",
    [(None, None),
     (("TOTAL", 89.5), {"total": 89.5}),
     (("FAIL", "FAIL MESSAGE"), {"failure": "FAIL MESSAGE"}),
     (("synca/__init__.py", 100.0),
      {"by_file": {"synca/__init__.py": 100.0}})])
def test_parse_table_row(patches, entry, expected_update):
    """Test _parse_table_row method with parametrized inputs."""
    combined_output = MagicMock()
    row = MagicMock()
    parser = coverage.CoverageParser(combined_output)
    coverage_data = {"total": 0.0, "by_file": {}}
    initial_data = coverage_data.copy()
    patched = patches(
        "CoverageParser._table_entry",
        prefix="synca.mcp.python.util.coverage")

    with patched as (m_table_entry,):
        m_table_entry.return_value = entry
        assert not parser._parse_table_row(coverage_data, row)

    assert m_table_entry.call_args == [(row,), {}]
    if expected_update is None:
        # Case 1: No update should happen
        assert coverage_data == initial_data
    elif "total" in expected_update:
        # Case 2: Total should be updated
        assert coverage_data["total"] == expected_update["total"]
        assert coverage_data["by_file"] == initial_data["by_file"]
    elif "by_file" in expected_update:
        # Case 3: by_file should be updated
        assert coverage_data["total"] == initial_data["total"]
        assert coverage_data["by_file"] == expected_update["by_file"]


@pytest.mark.parametrize(
    "line,expected_result",
    [("Name                   Stmts   Miss  Cover", True),
     ("                      Stmts   Miss  Cover", False),
     ("Name                          Miss  Cover", False),
     ("Name                   Stmts         Cover", False),
     ("Name                   Stmts   Miss       ", False),
     ("----------------------------------------", False)])
def test_coverage_table_start(line, expected_result):
    """Test _coverage_table_start method with parametrized inputs."""
    combined_output = MagicMock()
    parser = coverage.CoverageParser(combined_output)

    result = parser._coverage_table_start(line)
    assert result == expected_result


def test_table(patches, iters):
    """Test table property with parametrized inputs using the iters fixture."""
    # Set up mock data
    combined_output = (
        "Some output\n"
        "Name                   Stmts   Miss  Cover\n"
        "--------------------------------------------------\n"
        "file.py                    10      1    90%\n"
        "TOTAL                      10      1    90%"
    )
    parser = coverage.CoverageParser(combined_output)
    mock_rows = iters()

    # Create patches for methods used by table
    patched = patches(
        "CoverageParser._table_row",
        prefix="synca.mcp.python.util.coverage")

    with patched as (m_table_row,):
        m_table_row.side_effect = mock_rows + [None] * 10
        assert parser.table == mock_rows

    expected_calls = [
        [(line,), {}]
        for line in combined_output.splitlines()
    ]
    assert m_table_row.call_args_list == expected_calls


@pytest.mark.parametrize("error", [None, BaseException, ValueError])
@pytest.mark.parametrize(
    "row",
    [[],
     ["a", "b", "d%"],
     ["a", "b", "d"],
     ["a", "b", "c", "d%"],
     ["a", "b", "c", "d"],
     ["x", "y", "z", "a", "b", "c", "d"],
     ["x", "y", "z", "a", "b", "c", "d%"],
     ])
def test_table_entry(patches, error, row):
    """Test _table_entry method with parametrized inputs."""
    combined_output = MagicMock()
    parser = coverage.CoverageParser(combined_output)
    patched = patches(
        "float",
        prefix="builtins")
    expected = None
    success = (
        error != ValueError
        and len(row) > 3
        and row[-1].endswith("%"))

    with patched as (m_float,):
        if success:
            expected = " ".join(row[:-3]), m_float.return_value
        if error:
            m_float.side_effect = error("An error occurred")
        if success and error and error != ValueError:
            with pytest.raises(error):
                parser._table_entry(row)
        else:
            assert (
                parser._table_entry(row)
                == expected)


@pytest.mark.parametrize(
    "line,in_table,expected_result,table_start_result",
    [("Name                   Stmts   Miss  Cover",
      False, None, True),
     ("Name                   Stmts   Miss  Cover",
      True,
      ["Name", "Stmts", "Miss", "Cover"],
      True),
     ("--------------------------------------------------",
      True, None, False),
     ("Some arbitrary line", False, None, False),
     ("TOTAL                     10      1    90%",
      True,
      ["TOTAL", "10", "1", "90%"],
      False),
     ("", True, None, False),
     ("synca/__init__.py        10      1    90%",
      True,
      ["synca/__init__.py", "10", "1", "90%"],
      False)])
def test_table_row(
        patches, line, in_table, expected_result, table_start_result):
    """Test _table_row method with parametrized inputs."""
    combined_output = MagicMock()
    parser = coverage.CoverageParser(combined_output)
    parser._in_coverage_table = in_table
    initial_in_table = in_table
    patched = patches(
        "CoverageParser._coverage_table_start",
        prefix="synca.mcp.python.util.coverage")

    with patched as (m_table_start,):
        m_table_start.return_value = table_start_result
        result = parser._table_row(line)
        assert result == expected_result

    if not initial_in_table and table_start_result:
        assert parser._in_coverage_table is True
    elif initial_in_table and line == "":
        assert parser._in_coverage_table is False
