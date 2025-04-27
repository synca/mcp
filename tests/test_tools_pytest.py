"""Isolated tests for snake.mcp.server.tools.pytest."""

from unittest.mock import MagicMock

import pytest

from snake.mcp.server.tools.base import Tool
from snake.mcp.server.tools.pytest import PytestTool


def test_tools_pytest_constructor():
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
    "coverage_data",
    [None,
     {"total": 85.0, "by_file": {}},
     {"total": 85.0,
      "by_file": {},
      "failure": "FAIL Required coverage not reached"}])
def test_tools_pytest_parse_output(
        patches, stdout, stderr, returncode, coverage_data):
    """Test parse_output method with various combinations of inputs."""
    ctx = MagicMock()
    path = MagicMock()
    tool = PytestTool(ctx, path)
    test_summary = {
        "total": 5,
        "passed": 3,
        "failed": 2,
        "skipped": 0,
        "xfailed": 0,
        "xpassed": 0
    }
    combined_output = stdout + "\n" + stderr
    expected_issues = test_summary["failed"]
    if coverage_data and coverage_data.get("failure"):
        expected_issues += 1
    expected_msg = (
        "All tests passed successfully"
        if returncode == 0
        else combined_output)
    expected_data = {
        "test_summary": test_summary,
        "coverage": coverage_data or {"total": 0.0, "by_file": {}}
    }
    patched = patches(
        ("PytestTool._parse_test_summary",
         dict(return_value=test_summary)),
        ("PytestTool._parse_coverage_data",
         dict(return_value=coverage_data)),
        prefix="snake.mcp.server.tools.pytest")

    with patched as (m_summary, m_coverage):
        assert (
            tool.parse_output(stdout, stderr, returncode)
            == (expected_issues, expected_msg, expected_data))

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
def test_tools_pytest_parse_coverage_data(patches, output):
    """Test _parse_coverage_data method with various inputs."""
    ctx = MagicMock()
    path = MagicMock()
    tool = PytestTool(ctx, path)
    has_coverage = "Required test coverage" in output
    patched = patches(
        "CoverageParser",
        prefix="snake.mcp.server.tools.pytest")

    with patched as (m_parser,):
        assert (
            tool._parse_coverage_data(output)
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
def test_tools_pytest_parse_test_summary(output, expected_summary):
    """Test _parse_test_summary method with various inputs."""
    ctx = MagicMock()
    path = MagicMock()
    tool = PytestTool(ctx, path)
    result = tool._parse_test_summary(output)
    assert result == expected_summary
