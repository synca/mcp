"""Isolated tests for synca.mcp.fs_extra.tool.grep."""

import types
from unittest.mock import MagicMock, PropertyMock

import pytest

from synca.mcp.fs_extra.errors import FSCommandError
from synca.mcp.fs_extra.tool.base import UnixTool
from synca.mcp.fs_extra.tool.grep import GrepTool


def test_grep_tool_constructor():
    """Test GrepTool class initialization."""
    ctx = MagicMock()
    path = MagicMock()
    args = MagicMock()
    tool = GrepTool(ctx, path, args)
    assert isinstance(tool, UnixTool)
    assert tool.ctx == ctx
    assert tool._path_str == path
    assert tool._args == args
    assert tool.tool_name == "grep"
    assert "tool_name" not in tool.__dict__


@pytest.mark.parametrize("empty_args", [True, False])
@pytest.mark.parametrize("has_recursive", [True, False])
@pytest.mark.parametrize("has_path_arg", [True, False])
def test_grep_tool_validate_args(
        patches, empty_args, has_recursive, has_path_arg):
    """Test the validate_args method for GrepTool."""
    ctx = MagicMock()
    path = MagicMock()
    tool_args = MagicMock()
    tool = GrepTool(ctx, path, tool_args)
    mock_args = [MagicMock(), MagicMock()]
    test_args = MagicMock()
    test_args.__bool__.return_value = not empty_args
    test_args.__iter__.return_value = mock_args
    valid = (
        empty_args
        or has_recursive
        or has_path_arg)
    tool._recursive_flags = MagicMock()
    patched = patches(
        "any",
        "GrepTool.has_path_arg",
        ("GrepTool.err_stdin",
         dict(new_callable=PropertyMock)),
        prefix="synca.mcp.fs_extra.tool.grep")

    with patched as (m_any, m_path_arg, m_err_stdin):
        m_path_arg.return_value = has_path_arg
        m_any.return_value = has_recursive
        if valid:
            assert not tool.validate_args(test_args)
        else:
            with pytest.raises(FSCommandError) as e:
                tool.validate_args(test_args)

    assert (
        test_args.__bool__.call_args
        == [(), {}])
    if empty_args:
        assert not m_any.called
        assert not m_path_arg.called
        return
    any_gen = m_any.call_args[0][0]
    assert isinstance(any_gen, types.GeneratorType)
    assert (
        list(any_gen)
        == [False, False])
    assert (
        tool._recursive_flags.__contains__.call_args_list
        == [[(m, ), {}]
            for m in mock_args])
    if has_recursive:
        assert not m_path_arg.called
        return
    assert (
        m_path_arg.call_args
        == [(test_args, ), {}])
    if has_path_arg:
        return
    assert (
        e.value.args[0]
        == m_err_stdin.return_value)
