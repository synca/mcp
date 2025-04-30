"""Isolated tests for synca.mcp.python.tool.pytest."""

from unittest.mock import MagicMock

import pytest

from synca.mcp.common.tool import Tool
from synca.mcp.python.tool.pytest import PytestTool


def test_tool_pytest_constructor():
    """Test PytestTool class initialization."""
    ctx = MagicMock()
    path = MagicMock()
    tool = PytestTool(ctx, path)
    assert isinstance(tool, PytestTool)
    assert isinstance(tool, Tool)
    assert tool.ctx == ctx
    assert tool._path_str == path
    assert tool.tool_name == "pytest"
    assert "tool_name" not in tool.__dict__


@pytest.mark.parametrize(
    "stdout", ["", "Test output", "=== 1 passed in 0.1s ==="])
@pytest.mark.parametrize("stderr", ["", "Error output"])
@pytest.mark.parametrize("returncode", [0, 1, None])
@pytest.mark.parametrize(
    "coverage",
    [None,
     {"total": 85.0, "by_file": {}},
     {"total": 85.0,
      "by_file": {},
      "failure": "FAIL Required coverage not reached"}])
def test_tool_pytest_parse_output(
        patches, stdout, stderr, returncode, coverage):
    """Test parse_output method with various combinations of inputs."""
    ctx = MagicMock()
    path = MagicMock()
    tool = PytestTool(ctx, path)
    summary = {
        "total": 5,
        "passed": 3,
        "failed": 2,
        "skipped": 0,
        "xfailed": 0,
        "xpassed": 0
    }
    combined_output = stdout + "\n" + stderr
    expected_issues = summary["failed"]
    if coverage and coverage.get("failure"):
        expected_issues += 1
    expected_msg = (
        "All tests passed successfully"
        if returncode == 0
        else combined_output)
    expected_data = {
        "summary": summary,
        "coverage": coverage or {"total": 0.0, "by_file": {}}
    }
    patched = patches(
        ("PytestTool._parse_summary",
         dict(return_value=summary)),
        ("PytestTool._parse_coverage",
         dict(return_value=coverage)),
        prefix="synca.mcp.python.tool.pytest")

    with patched as (m_summary, m_coverage):
        assert (
            tool.parse_output(stdout, stderr, returncode)
            == (returncode or 0, expected_issues, expected_msg, expected_data))

    assert (
        m_summary.call_args
        == [(combined_output,), {}])
    assert (
        m_coverage.call_args
        == [(combined_output,), {}])


@pytest.mark.parametrize(
    "output",
    ["",
     "Test output without coverage",
     "=== 1 passed in 0.1s ===",
     "Required test coverage of 95% not reached",
     """Name                 Stmts   Miss  Cover   Missing
--------------------------------------------------
package/__init__.py     10      2    80%   5-7
TOTAL                   10      2    80%
FAIL Required test coverage of 95% not reached."""])
def test_tool_pytest_parse_coverage(patches, output):
    """Test _parse_coverage method with various inputs."""
    ctx = MagicMock()
    path = MagicMock()
    tool = PytestTool(ctx, path)
    has_coverage = "Required test coverage" in output
    patched = patches(
        "CoverageParser",
        prefix="synca.mcp.python.tool.pytest")

    with patched as (m_parser,):
        assert (
            tool._parse_coverage(output)
            == (m_parser.return_value.data
                if has_coverage
                else None))

    if not has_coverage:
        assert not m_parser.called
        return
    assert (
        m_parser.call_args
        == [(output,), {}])


@pytest.mark.parametrize(
    "output,expected_summary",
    [("", {
         "total": 0, "passed": 0, "failed": 0,
         "skipped": 0, "xfailed": 0, "xpassed": 0
     }),
     ("Test output", {
         "total": 0, "passed": 0, "failed": 0,
         "skipped": 0, "xfailed": 0, "xpassed": 0
     }),
     ("=== no tests ran in 0.1s ===", {
         "total": 0, "passed": 0, "failed": 0,
         "skipped": 0, "xfailed": 0, "xpassed": 0
     }),
     ("=== 1 passed in 0.1s ===", {
         "total": 1, "passed": 1, "failed": 0,
         "skipped": 0, "xfailed": 0, "xpassed": 0
     }),
     ("=== 1 failed in 0.1s ===", {
         "total": 1, "passed": 0, "failed": 1,
         "skipped": 0, "xfailed": 0, "xpassed": 0
     }),
     ("=== 1 skipped in 0.1s ===", {
         "total": 1, "passed": 0, "failed": 0,
         "skipped": 1, "xfailed": 0, "xpassed": 0
     }),
     ("=== 1 xfailed in 0.1s ===", {
         "total": 1, "passed": 0, "failed": 0,
         "skipped": 0, "xfailed": 1, "xpassed": 0
     }),
     ("=== 1 xpassed in 0.1s ===", {
         "total": 1, "passed": 0, "failed": 0,
         "skipped": 0, "xfailed": 0, "xpassed": 1
     }),
     ("=== 5 passed, 3 failed, 2 skipped, 1 xfailed in 1.5s ===", {
         "total": 11, "passed": 5, "failed": 3,
         "skipped": 2, "xfailed": 1, "xpassed": 0
     })])
def test_tool_pytest_parse_summary(output, expected_summary):
    """Test _parse_summary method with various inputs."""
    ctx = MagicMock()
    path = MagicMock()
    tool = PytestTool(ctx, path)
    result = tool._parse_summary(output)
    assert result == expected_summary
