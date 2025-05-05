"""Isolated tests for synca.mcp.cargo.tool.check."""

from unittest.mock import MagicMock

import pytest

from synca.mcp.cargo.tool.base import CargoTool
from synca.mcp.cargo.tool.check import CheckTool


def test_tool_check_constructor():
    """Test CheckTool class initialization."""
    ctx = MagicMock()
    path = MagicMock()
    args = MagicMock()
    tool = CheckTool(ctx, path, args)
    assert isinstance(tool, CheckTool)
    assert isinstance(tool, CargoTool)
    assert tool.ctx == ctx
    assert tool._path_str == path
    assert tool.tool_name == "check"
    assert "tool_name" not in tool.__dict__
    assert tool._args == args


@pytest.mark.parametrize("return_code", [0, 1, None])
@pytest.mark.parametrize("warnings", [[], ["warning: unused variable"]])
@pytest.mark.parametrize("errors", [[], ["error: mismatched types"]])
@pytest.mark.parametrize(
    "resolutions",
    [[], ["run `cargo fix` to apply 1 suggestion"]])
@pytest.mark.parametrize("has_finished", [True, False])
def test_check_parse_output(
        patches, return_code, warnings, errors, resolutions, has_finished):
    """Test the parse_output method of CheckTool with various inputs."""
    ctx = MagicMock()
    path = MagicMock()
    args = MagicMock()
    tool = CheckTool(ctx, path, args)
    stdout = "Checking crate...\n"
    if has_finished:
        stdout += "Finished dev [unoptimized + debuginfo]\n"
    stderr = ""
    expected_issues_count = len(warnings) + len(errors)
    all_good = (
        expected_issues_count == 0
        and return_code == 0
        and has_finished)

    # Build expected info dictionary outside patched context
    expected_info = {}
    if warnings:
        expected_info["warnings_count"] = len(warnings)
        expected_info["warning_messages"] = warnings
    if errors:
        expected_info["errors_count"] = len(errors)
        expected_info["errors"] = errors
    if resolutions:
        expected_info["resolutions"] = resolutions

    patched = patches(
        "CheckTool.parse_issues",
        prefix="synca.mcp.cargo.tool.check")

    with patched as (m_parse_issues,):
        m_parse_issues.return_value = (warnings, errors, resolutions)
        result = tool.parse_output(stdout, stderr, return_code)
        assert (
            result
            == (return_code,
                ("No issues found"
                 if all_good
                 else f"Issues found: {expected_issues_count}"),
                "" if all_good else stdout + "\n" + stderr,
                expected_info))

    assert (
        m_parse_issues.call_args
        == [(stdout + "\n" + stderr,), {}])


@pytest.mark.parametrize(
    "combined_output,expected",
    [("\n",
      ([], [], [])),
     ("warning: unused variable",
      (["warning: unused variable"], [], [])),
     ("error: mismatched types",
      ([], ["error: mismatched types"], [])),
     ("run `cargo fix --bin \"project\"` to apply 1 suggestion",
      ([], [], ["run `cargo fix --bin \"project\"` to apply 1 suggestion"])),
     ("Checking crate...\n"
      "Compiling lib v0.1.0\n"
      "Warning: capital letter\n"
      "warning: unused variable\n"
      "warning: redundant clone\n"
      "Finished",
      (["warning: unused variable",
        "warning: redundant clone"],
       [],
       [])),
     ("error: expected struct Foo\n"
      "error: mismatched types\n"
      "Help: try using a different type",
      ([],
       ["error: expected struct Foo",
        "error: mismatched types"],
       [])),
     ("run `cargo fix --bin \"project\"` to apply 1 suggestion\n"
      "cargo check --fix --allow-dirty",
      ([],
       [],
       ["run `cargo fix --bin \"project\"` to apply 1 suggestion"])),
     ("warning: unused imports\n"
      "error: missing field\n"
      "run `cargo fix` to apply some fixes\n"
      "Some other text",
      (["warning: unused imports"],
       ["error: missing field"],
       ["run `cargo fix` to apply some fixes"]))])
def test_check_parse_issues(combined_output, expected):
    """Test the _parse_issues method with various inputs."""
    ctx = MagicMock()
    path = MagicMock()
    args = MagicMock()
    tool = CheckTool(ctx, path, args)
    assert (
        tool.parse_issues(combined_output)
        == expected)
