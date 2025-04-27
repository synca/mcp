"""Isolated tests for synca.mcp.cargo.tool.test."""

from unittest.mock import MagicMock

import pytest

from synca.mcp.cargo.tool.base import Tool, CargoTool
from synca.mcp.cargo.tool.test import TestTool


def test_tool_test_constructor():
    """Test TestTool class initialization."""
    ctx = MagicMock()
    path = MagicMock()
    tool = TestTool(ctx, path)
    assert isinstance(tool, TestTool)
    assert isinstance(tool, CargoTool)
    assert isinstance(tool, Tool)
    assert tool.ctx == ctx
    assert tool._path_str == path
    assert tool.tool_name == "test"
    assert "tool_name" not in tool.__dict__


@pytest.mark.parametrize("return_code", [0, 1, None])
@pytest.mark.parametrize("warnings", [[], ["warning: unused variable"]])
@pytest.mark.parametrize("errors", [[], ["error: mismatched types"]])
@pytest.mark.parametrize("notes", [[], ["note: consider using let"]])
@pytest.mark.parametrize(
    "summary",
    [{"total_tests": 5, "passed": 5, "failed": 0, "status": "passed"},
     {"total_tests": 5, "passed": 3, "failed": 2, "status": "failed"},
     {"status": "unknown"}])
def test_tool_test_parse_output(
        patches, return_code, warnings, errors, notes, summary):
    """Test parse_output method with various inputs."""
    ctx = MagicMock()
    path = MagicMock()
    tool = TestTool(ctx, path)
    stdout = "Test output"
    stderr = "Test error output"
    warnings_count = len(warnings)
    errors_count = len(errors)
    test_failures = summary.get("failed", 0)
    issues_count = test_failures + errors_count + warnings_count
    all_good = return_code == 0 and issues_count == 0
    expected_message = (
        "All tests passed successfully"
        if all_good
        else "Some tests failed")
    expected_info = {}
    if warnings:
        expected_info["warnings_count"] = warnings_count
        expected_info["warnings"] = warnings
    if errors:
        expected_info["errors_count"] = errors_count
        expected_info["errors"] = errors
    if notes:
        expected_info["notes"] = notes
    expected_info["summary"] = summary
    patched = patches(
        "TestTool.parse_issues",
        "TestTool._extract_summary",
        prefix="synca.mcp.cargo.tool.test")

    with patched as (m_parse_issues, m_extract_summary):
        m_parse_issues.return_value = (warnings, errors, notes)
        m_extract_summary.return_value = summary
        assert (
            tool.parse_output(stdout, stderr, return_code)
            == (
                return_code,
                issues_count,
                (expected_message
                 if all_good
                 else stdout + "\n" + stderr),
                expected_info
            ))

    assert (
        m_parse_issues.call_args
        == [(stdout + "\n" + stderr,), {}])
    assert (
        m_extract_summary.call_args
        == [(stdout + "\n" + stderr,), {}])


@pytest.mark.parametrize(
    "combined_output,expected",
    [(("running 5 tests\n"
       "test test_a ... ok\n"
       "test result: ok. 5 passed; 0 failed"),
      {"total_tests": 5,
       "passed": 5,
       "failed": 0,
       "status": "passed"}),
     (("running 5 tests\n"
       "test test_a ... ok\n"
       "test test_b ... FAILED\n"
       "test result: FAILED. 3 passed; 2 failed"),
      {"total_tests": 5,
       "passed": 3,
       "failed": 2,
       "status": "failed"}),
     ("running tests\nsome other output",
      {"status": "unknown"}),
     ("",
      {"status": "unknown"})])
def test_tool_test_extract_summary(patches, combined_output, expected):
    """Test _extract_summary method with various outputs."""
    ctx = MagicMock()
    path = MagicMock()
    tool = TestTool(ctx, path)
    patched = patches(
        "TestTool._parse_success_result",
        "TestTool._parse_failure_result",
        prefix="synca.mcp.cargo.tool.test")

    with patched as (m_parse_success, m_parse_failure):
        m_parse_success.side_effect = (
            lambda line: expected if "test result: ok." in line else None)
        m_parse_failure.side_effect = (
            lambda line: expected if "test result: FAILED" in line else None)
        assert (
            tool._extract_summary(combined_output)
            == expected)

    success_calls = [
        [(line,), {}]
        for line in combined_output.splitlines()
        if "test result: ok." in line]
    failure_calls = [
        [(line,), {}]
        for line in combined_output.splitlines()
        if "test result: FAILED" in line]
    assert (
        m_parse_success.call_args_list
        == success_calls)
    assert (
        m_parse_failure.call_args_list
        == failure_calls)


@pytest.mark.parametrize(
    "error",
    [None, IndexError, ValueError, BaseException])
@pytest.mark.parametrize(
    "line,expected_count",
    [("test result: ok. 5 passed; 0 failed", 5),
     ("test result: ok. 10 passed; 0 failed; 2 ignored", 10)])
def test_tool_test_parse_success_result(patches, error, line, expected_count):
    """Test _parse_success_result with various inputs and error types."""
    ctx = MagicMock()
    path = MagicMock()
    tool = TestTool(ctx, path)
    mock_line = MagicMock()
    parts = line.split()
    expected = (
        {"total_tests": expected_count,
         "passed": expected_count,
         "failed": 0,
         "status": "passed"}
        if error is None
        else None)
    mock_line.split.return_value = (
        parts[:3]
        if error is IndexError
        else parts)
    patched = patches(
        "int",
        prefix="synca.mcp.cargo.tool.test")

    with patched as (m_int,):
        m_int.return_value = expected_count
        if error is ValueError:
            m_int.side_effect = ValueError("invalid literal")
        elif error is BaseException:
            m_int.side_effect = BaseException("unexpected")
        if error and error not in [IndexError, ValueError]:
            with pytest.raises(BaseException):
                tool._parse_success_result(mock_line)
        else:
            assert (
                tool._parse_success_result(mock_line)
                == expected)

    assert (
        mock_line.split.call_args
        == [(), {}])
    if error == IndexError:
        assert not m_int.called
        return
    assert (
        m_int.call_args
        == [(parts[3],), {}])


@pytest.mark.parametrize(
    "error",
    [None, IndexError, ValueError, BaseException])
@pytest.mark.parametrize(
    "line,expected_passed,expected_failed",
    [("test result: FAILED. 3 passed; 2 failed;", 3, 2),
     ("test result: FAILED. 0 passed; 10 failed; 2 ignored", 0, 10)])
def test_tool_test_parse_failure_result(
        patches, error, line, expected_passed, expected_failed):
    """Test _parse_failure_result with various inputs and error types."""
    ctx = MagicMock()
    path = MagicMock()
    tool = TestTool(ctx, path)
    mock_line = MagicMock()
    parts = line.split()
    expected_total = expected_passed + expected_failed
    expected = (
        {"total_tests": expected_total,
         "passed": expected_passed,
         "failed": expected_failed,
         "status": "failed"}
        if error is None
        else None)
    mock_line.split.return_value = parts
    if error is IndexError:
        mock_line.split.side_effect = lambda: []
    patched = patches(
        "int",
        prefix="synca.mcp.cargo.tool.test")
    counter = MagicMock()
    counter.count = 0

    def _int(value):
        counter.count += 1
        return (
            expected_failed
            if counter.count == 1
            else expected_passed)

    with patched as (m_int,):
        m_int.side_effect = _int
        if error is ValueError:
            m_int.side_effect = error("invalid literal")
        elif error is BaseException:
            m_int.side_effect = error("unexpected")
        if error and error not in [IndexError, ValueError]:
            with pytest.raises(BaseException):
                tool._parse_failure_result(mock_line)
        else:
            assert (
                tool._parse_failure_result(mock_line)
                == expected)

    assert (
        mock_line.split.call_args
        == [(), {}])
