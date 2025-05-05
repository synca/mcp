"""Isolated tests for synca.mcp.cargo.tool.base."""

from unittest.mock import MagicMock, PropertyMock

import pytest

from synca.mcp.common.tool import CLITool
from synca.mcp.cargo.tool.base import CargoTool


def test_tool_base_constructor():
    """Test CargoTool class initialization."""
    ctx = MagicMock()
    path = MagicMock()
    args = MagicMock()
    tool = CargoTool(ctx, path, args)
    assert isinstance(tool, CargoTool)
    assert isinstance(tool, CLITool)
    assert tool.ctx == ctx
    assert tool._path_str == path
    assert tool._args == args


def test_tool_path(patches):
    """Test the tool_path property."""
    ctx = MagicMock()
    path = MagicMock()
    args = MagicMock()
    tool = CargoTool(ctx, path, args)

    patched = patches(
        ("CargoTool.tool_name",
         dict(new_callable=PropertyMock)),
        prefix="synca.mcp.cargo.tool.base")

    with patched as (m_tool_name,):
        assert tool.tool_path == m_tool_name.return_value

    assert "tool_path" not in tool.__dict__


@pytest.mark.parametrize("is_project", [True, False])
def test_validate_path(patches, is_project):
    """Test validate_path method."""
    ctx = MagicMock()
    path_str = MagicMock()
    args = MagicMock()
    tool = CargoTool(ctx, path_str, args)
    path = MagicMock()
    patched = patches(
        "super",
        prefix="synca.mcp.cargo.tool.base")

    with patched as (m_super,):
        path.__truediv__.return_value.exists.return_value = is_project
        if is_project:
            assert not tool.validate_path(path)
        else:
            with pytest.raises(FileNotFoundError) as e:
                tool.validate_path(path)

    assert (
        m_super.return_value.validate_path.call_args
        == [(path,), {}])
    assert (
        path.__truediv__.call_args
        == [("Cargo.toml",), {}])
    assert (
        path.__truediv__.return_value.exists.call_args
        == [(), {}])
    if not is_project:
        assert (
            str(e.value)
            == (f"Path '{path}' is not a valid Rust project "
                "(no Cargo.toml found)"))


@pytest.mark.parametrize(
    "additional_errors",
    [True, False])
@pytest.mark.parametrize(
    "combined_output,expected_base,expected_with_additional",
    [("",
      ([], [], []),
      ([], [], [])),
     ("warning: unused variable\n  some context",
      (["warning: unused variable"], [], []),
      (["warning: unused variable"], [], [])),
     ("error: mismatched types\n  some context",
      ([], ["error: mismatched types"], []),
      ([], ["error: mismatched types"], [])),
     ("custom error pattern detected in output\n  some context",
      ([], [], []),
      ([], ["custom error pattern detected in output"], [])),
     ("note: consider adding type annotation\n  some context",
      ([], [], ["note: consider adding type annotation"]),
      ([], [], ["note: consider adding type annotation"])),
     ("warning: unused import\n"
      "error: missing semicolon\n"
      "note: expected `;` here\n"
      "  some other output\n"
      "warning: another warning",
      (["warning: unused import",
        "warning: another warning"],
       ["error: missing semicolon"],
       ["note: expected `;` here"]),
      (["warning: unused import",
        "warning: another warning"],
       ["error: missing semicolon"],
       ["note: expected `;` here"])),
     ("\n"
      "Compiling my_crate v0.1.0\n"
      "warning: unused variable\n"
      "\n"
      "custom error pattern in logs\n"
      "error: type mismatch",
      (["warning: unused variable"],
       ["error: type mismatch"],
       []),
      (["warning: unused variable"],
       ["custom error pattern in logs", "error: type mismatch"],
       []))])
def test_base_parse_issues(
        combined_output, expected_base, expected_with_additional,
        additional_errors):
    """Test _parse_issues method extracts warnings, errors,
    and notes correctly.
    """
    ctx = MagicMock()
    path = MagicMock()
    args = MagicMock()
    tool = CargoTool(ctx, path, args)
    kwargs = (
        dict(additional_errors=["custom error pattern"])
        if additional_errors
        else {})

    assert (
        tool.parse_issues(combined_output, **kwargs)
        == (expected_with_additional
            if additional_errors
            else expected_base))
