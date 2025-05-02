"""Isolated tests for synca.mcp.fs_extra.tool.base."""

from unittest.mock import MagicMock, PropertyMock

import pytest

from synca.mcp.common.tool import CLITool
from synca.mcp.fs_extra.tool.base import UnixTool


def test_unix_tool_constructor():
    """Test UnixTool class initialization."""
    ctx = MagicMock()
    path = MagicMock()
    args = MagicMock()
    tool = UnixTool(ctx, path, args)
    assert isinstance(tool, CLITool)
    assert tool.ctx == ctx
    assert tool._path_str == path
    assert tool.args == args


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
    "command_args",
    [None,
     [MagicMock()],
     [MagicMock(), MagicMock()]])
def test_unix_tool_command(patches, command_args):
    """Test command with parametrized arguments."""
    ctx = MagicMock()
    path = MagicMock()
    args = MagicMock()
    tool = UnixTool(ctx, path, args)
    patched = patches(
        ("UnixTool.tool_path",
         dict(new_callable=PropertyMock)),
        ("UnixTool.config_args",
         dict(new_callable=PropertyMock)),
        prefix="synca.mcp.fs_extra.tool.base")

    with patched as (m_tool_path, m_config_args):
        assert (
            tool.command(command_args)
            == (m_tool_path.return_value,
                *m_config_args.return_value,
                *(args or [])))

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
