"""Isolated tests for synca.mcp.cargo.tool.fmt."""

from unittest.mock import MagicMock

import pytest

from synca.mcp.cargo.tool.base import CargoTool
from synca.mcp.cargo.tool.fmt import FmtTool


def test_tool_fmt_constructor():
    """Test FmtTool class initialization."""
    ctx = MagicMock()
    path = MagicMock()
    tool = FmtTool(ctx, path)
    assert isinstance(tool, FmtTool)
    assert isinstance(tool, CargoTool)
    assert tool.ctx == ctx
    assert tool._path_str == path
    assert tool.tool_name == "fmt"
    assert "tool_name" not in tool.__dict__


@pytest.mark.parametrize("has_diffs", [True, False])
@pytest.mark.parametrize("return_code", [0, 1, None])
@pytest.mark.parametrize("empty_output", [True, False])
def test_fmt_parse_output(patches, has_diffs, return_code, empty_output):
    """Test the parse_output method of FmtTool."""
    ctx = MagicMock()
    path = MagicMock()
    tool = FmtTool(ctx, path)
    stderr = ""
    stdout = (
        ("Diff in src/main.rs at line 10:\n"
         "-    let x = 5;\n"
         "+    let x = 5;")
        if (has_diffs
            and not empty_output)
        else "")
    combined_output = stdout + "\n" + stderr
    warnings = ["warning: test warning"]
    errors = ["error: test error"]
    notes = ["note: test note"]
    expected_info = {}
    expected_info["needs_formatting"] = (
        has_diffs
        and not empty_output
        and return_code != 0)
    expected_info["warnings_count"] = len(warnings)
    expected_info["warnings"] = warnings
    expected_info["errors_count"] = len(errors)
    expected_info["errors"] = errors
    expected_info["notes"] = notes
    message = (
        "Code is properly formatted"
        if return_code == 0
        else "Cargo fmt failed")
    patched = patches(
        "FmtTool.parse_issues",
        prefix="synca.mcp.cargo.tool.fmt")

    with patched as (m_parse_issues,):
        m_parse_issues.return_value = (warnings, errors, notes)
        assert (
            tool.parse_output(stdout, stderr, return_code)
            == (return_code or 0,
                message,
                combined_output.strip(),
                expected_info))

    assert (
        m_parse_issues.call_args
        == [(combined_output,), {}])
