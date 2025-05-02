"""Isolated tests for synca.mcp.cargo.tool.clippy."""

from unittest.mock import MagicMock

import pytest

from synca.mcp.cargo.tool.base import CargoTool
from synca.mcp.cargo.tool.clippy import ClippyTool


def test_tool_clippy_constructor():
    """Test ClippyTool class initialization."""
    ctx = MagicMock()
    path = MagicMock()
    tool = ClippyTool(ctx, path)
    assert isinstance(tool, ClippyTool)
    assert isinstance(tool, CargoTool)
    assert tool.ctx == ctx
    assert tool._path_str == path
    assert tool.tool_name == "clippy"
    assert "tool_name" not in tool.__dict__


@pytest.mark.parametrize("args", [True, False])
def test_tool_clippy_command(args):
    """Test the custom command building for clippy."""
    ctx = MagicMock()
    path = MagicMock()
    tool = ClippyTool(ctx, path)
    kwargs = {}
    if args:
        kwargs["args"] = MagicMock()
    assert (
        tool.command(**kwargs)
        == ("cargo", "clippy"))


@pytest.mark.parametrize("return_code", [0, 1, None])
@pytest.mark.parametrize("warnings", [[], ["warning: unused variable"]])
@pytest.mark.parametrize("errors", [[], ["error: mismatched types"]])
@pytest.mark.parametrize(
    "resolutions",
    [[], ["cargo clippy --fix can probably fix this"]])
@pytest.mark.parametrize("has_finished", [True, False])
def test_clippy_parse_output(
        patches, return_code, warnings, errors, resolutions, has_finished):
    ctx = MagicMock()
    path = MagicMock()
    tool = ClippyTool(ctx, path)
    stdout = "Checking crate...\n"
    if has_finished:
        stdout += "Finished dev [unoptimized + debuginfo]\n"
    stderr = ""
    issues_count = len(warnings) + len(errors)
    all_good = (
        issues_count == 0
        and return_code == 0
        and has_finished)
    expected_calls = []
    if warnings:
        expected_calls.append(((warnings, "warning"), {}))
    if errors:
        expected_calls.append(((errors, "error"), {}))
    patched = patches(
        "ClippyTool.parse_issues",
        "ClippyTool._categorize_issues",
        prefix="synca.mcp.cargo.tool.clippy")

    with patched as (m_parse_issues, m_categorize_issues):
        m_parse_issues.return_value = (warnings, errors, resolutions)
        m_categorize_issues.return_value = {"category": 1}
        result = tool.parse_output(stdout, stderr, return_code)
        expected_info = {}
        if warnings:
            expected_info["warnings_count"] = len(warnings)
            expected_info["warning_types"] = m_categorize_issues.return_value
        if errors:
            expected_info["errors_count"] = len(errors)
            expected_info["error_types"] = m_categorize_issues.return_value
        if resolutions:
            expected_info["resolutions"] = resolutions
        assert (
            result
            == (return_code or 0,
                ("No issues found"
                 if all_good
                 else f"Issues found: {issues_count}"),
                (""
                 if all_good
                 else stdout + "\n" + stderr),
                expected_info))

    assert (
        m_parse_issues.call_args
        == [(stdout + "\n" + stderr,), {}])
    assert (
        m_categorize_issues.call_args_list
        == expected_calls)


@pytest.mark.parametrize(
    "combined_output,expected",
    [("",
      ([], [], [])),
     ("warning: unused variable",
      (["warning: unused variable"], [], [])),
     ("error: mismatched types",
      ([], ["error: mismatched types"], [])),
     ("cargo clippy --fix can fix this",
      ([], [], ["cargo clippy --fix can fix this"])),
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
     ("cargo clippy --fix can fix this\n"
      "cargo clippy --fix --allow-dirty",
      ([],
       [],
       ["cargo clippy --fix can fix this",
        "cargo clippy --fix --allow-dirty"])),
     ("warning: unused imports\n"
      "error: missing field\n"
      "cargo clippy --fix can fix some issues\n"
      "Some other text",
      (["warning: unused imports"],
       ["error: missing field"],
       ["cargo clippy --fix can fix some issues"]))])
def test_clippy_parse_issues(combined_output, expected):
    ctx = MagicMock()
    path = MagicMock()
    tool = ClippyTool(ctx, path)
    assert (
        tool.parse_issues(combined_output)
        == expected)


@pytest.mark.parametrize(
    "issues,issue_type,expected",
    [([],
      "warning",
      {}),
     (["warning: unused variable"],
      "warning",
      {"unused variable": 1}),
     (["warning: unused variable",
       "warning: unused variable"],
      "warning",
      {"unused variable": 2}),
     (["warning: unused_variables: x is not used"],
      "warning",
      {"unused_variables": 1}),
     (["warning: redundant_clone: x.clone()",
       "warning: unused_variables: y is not used",
       "warning: redundant_clone: y.clone()"],
      "warning",
      {"redundant_clone": 2, "unused_variables": 1}),
     (["error: mismatched types: expected i32, found String"],
      "error",
      {"mismatched types": 1}),
     (["error: no field `foo` on type `Bar`",
       "error: no method named `baz` found"],
      "error",
      {"no field `foo` on type `Bar`": 1, "no method named `baz` found": 1}),
     # Test malformed issues
     (["malformed issue without separator"],
      "warning",
      {}),
     (["error something without proper separator"],
      "error",
      {})])
def test_clippy_categorize_issues(issues, issue_type, expected):
    ctx = MagicMock()
    path = MagicMock()
    tool = ClippyTool(ctx, path)
    assert (
        tool._categorize_issues(issues, issue_type)
        == expected)
