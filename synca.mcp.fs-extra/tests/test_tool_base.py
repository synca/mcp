"""Isolated tests for synca.mcp.fs_extra.tool.base."""

from unittest.mock import MagicMock, PropertyMock

import pytest

from synca.mcp.common.tool import CLITool
from synca.mcp.fs_extra.errors import FSCommandError
from synca.mcp.fs_extra.tool.base import UnixTool, UnixSliceTool


# TODO: move these to common

def test_unix_tool_args(patches):
    ctx = MagicMock()
    path = MagicMock()
    args = MagicMock()
    tool = UnixTool(ctx, path, args)
    patched = patches(
        "super",
        "UnixTool.validate_args",
        prefix="synca.mcp.fs_extra.tool.base")

    with patched as (m_super, m_validate):
        assert (
            tool.args
            == m_super.return_value.args)

    assert (
        m_validate.call_args
        == [(m_super.return_value.args, ), {}])
    assert "args" not in tool.__dict__


def test_unix_tool_validate_args(patches):
    ctx = MagicMock()
    path = MagicMock()
    args = MagicMock()
    tool = UnixTool(ctx, path, args)
    assert not tool.validate_args(args)


def test_unix_tool_constructor():
    """Test UnixTool class initialization."""
    ctx = MagicMock()
    path = MagicMock()
    args = MagicMock()
    tool = UnixTool(ctx, path, args)
    assert isinstance(tool, CLITool)
    assert tool.ctx == ctx
    assert tool._path_str == path
    assert tool._args == args


def test_unix_tool_err_stdin(patches):
    """Test the tool_path property."""
    ctx = MagicMock()
    path = MagicMock()
    args = MagicMock()
    tool = UnixTool(ctx, path, args)
    patched = patches(
        ("UnixTool.tool_name",
         dict(new_callable=PropertyMock)),
        prefix="synca.mcp.fs_extra.tool.base")
    with patched as (m_tool_name,):
        assert (
            tool.err_stdin
            == (f"{m_tool_name.return_value.capitalize.return_value} "
                "command requires file "
                "arguments. The command might be expecting input from stdin, "
                "which is not supported. "
                "Please provide at least one explicit file path in your "
                f"{m_tool_name.return_value} command."))

    assert "err_stdin" not in tool.__dict__


@pytest.mark.parametrize(
    "test_args,expected",
    [([], False),
     (["-a", "file.txt"], False),
     (["-x", "value", "file.txt"], True),
     (["-y", "file.txt"], True),
     (["file.txt"], True),
     (["-a", "value", "-x", "value2"], False),
     (["-a", "value", "--other", "file.txt"], True),
     (["-a", "value", "-x", "value2",
       "--foo", "value3", "--bar", "value4", "file.txt"],
      True),
     (["-a", "value", "-x", "value2", "--foo", "value3",
       "--bar", "value4"],
      False)])
def test_unix_tool_has_path_arg(patches, test_args, expected):
    """Test the has_path_arg method."""
    ctx = MagicMock()
    path = MagicMock()
    args = MagicMock()
    tool = UnixTool(ctx, path, args)
    flags_with_args = ("-a", "-x", "--foo", "--bar")
    patched = patches(
        ("UnixTool.flags_with_args",
         dict(new_callable=PropertyMock)),
        prefix="synca.mcp.fs_extra.tool.base")

    with patched as (m_flags_with_args,):
        m_flags_with_args.return_value = flags_with_args
        assert (
            tool.has_path_arg(test_args)
            is expected)


def test_unix_tool_tool_path(patches):
    """Test the tool_path property."""
    ctx = MagicMock()
    path = MagicMock()
    args = MagicMock()
    tool = UnixTool(ctx, path, args)
    patched = patches(
        ("UnixTool.tool_name",
         dict(new_callable=PropertyMock)),
        prefix="synca.mcp.fs_extra.tool.base")

    with patched as (m_tool_name,):
        assert tool.tool_path == m_tool_name.return_value

    assert "tool_path" not in tool.__dict__


@pytest.mark.parametrize(
    "stdout",
    ["test output",
     "",
     "line1\nline2\nline3",
     "line1\nline2\nline3\n"])
@pytest.mark.parametrize(
    "stderr",
    ["",
     "error output"])
@pytest.mark.parametrize(
    "return_code",
    [0, 1])
def test_unix_tool_parse_output(
        patches,
        stdout,
        stderr,
        return_code):
    """Test parse_output method with various outputs."""
    ctx = MagicMock()
    path = MagicMock()
    args = MagicMock()
    tool = UnixTool(ctx, path, args)
    tool.success_message = "Success message"
    tool.failure_message = "Failure message"
    if return_code == 0:
        line_count = stdout.count('\n')
        if stdout and not stdout.endswith('\n'):
            line_count += 1
        expected = (
            0,
            "Success message",
            stdout,
            {
                "lines_read": line_count,
                "bytes_read": len(stdout.encode('utf-8'))
            })
    else:
        expected = (
            return_code,
            "Failure message",
            stderr if stderr else "Unknown error occurred",
            {})
    assert (
        tool.parse_output(stdout, stderr, return_code)
        == expected)


@pytest.mark.parametrize("empty_args", [True, False])
@pytest.mark.parametrize("has_path", [True, False])
def test_unix_slice_tool_validate_args(patches, empty_args, has_path):
    """Test UnixSliceTool.validate_args method."""
    ctx = MagicMock()
    path = MagicMock()
    args = MagicMock()
    tool = UnixSliceTool(ctx, path, args)
    test_args = MagicMock()
    test_args.__bool__.return_value = not empty_args
    patched = patches(
        ("UnixSliceTool.has_path_arg",
         dict(return_value=has_path)),
        ("UnixSliceTool.err_stdin",
         dict(new_callable=PropertyMock)),
        prefix="synca.mcp.fs_extra.tool.base")

    with patched as (m_has_path, m_err_stdin):
        if empty_args or not has_path:
            with pytest.raises(FSCommandError) as e:
                tool.validate_args(test_args)
        else:
            assert tool.validate_args(test_args) is None

    assert (
        test_args.__bool__.call_args
        == [(), {}])
    if empty_args:
        assert not m_has_path.called
        return
    assert (
        m_has_path.call_args
        == [(test_args,), {}])
    if not has_path:
        assert (
            e.value.args[0]
            == m_err_stdin.return_value)
