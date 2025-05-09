"""Isolated tests for synca.mcp.fs_extra.tool.sed."""

from unittest.mock import MagicMock, PropertyMock

import pytest

from synca.mcp.fs_extra.errors import FSCommandError
from synca.mcp.fs_extra.tool.base import UnixTool
from synca.mcp.fs_extra.tool.sed import SedTool


def test_sed_tool_constructor():
    """Test SedTool class initialization."""
    ctx = MagicMock()
    path = MagicMock()
    args = MagicMock()
    tool = SedTool(ctx, path, args)
    assert isinstance(tool, UnixTool)
    assert tool.ctx == ctx
    assert tool._path_str == path
    assert tool._args == args
    assert tool.success_message == "Successfully ran the sed command"
    assert tool.flags_with_args == ('-e', '--expression', '-f', '--file')


def test_sed_tool_tool_name():
    """Test the tool_name property returns the correct tool name."""
    ctx = MagicMock()
    path = MagicMock()
    args = MagicMock()
    tool = SedTool(ctx, path, args)
    assert tool.tool_name == "sed"
    assert "tool_name" not in tool.__dict__


@pytest.mark.parametrize(
    "args,invalid",
    [([], True),
     (["s/old/new/"], True),
     (["-e", "s/old/new/"], True),
     (["-f", "script.sed"], False),
     (["-e", "s/old/new/", "-e", "s/a/b/"], True),
     (["s/old/new/", "file.txt"], False),
     (["-e", "s/old/new/", "file.txt"], False),
     (["-e", "s/old/new/", "file1.txt", "file2.txt"], False)])
def test_sed_tool_validate_args(patches, args, invalid):
    """Test SedTool validate_args method."""
    ctx = MagicMock()
    path = MagicMock()
    tool_args = MagicMock()
    tool = SedTool(ctx, path, tool_args)
    patched = patches(
        "SedTool.has_path_arg",
        ("SedTool.err_stdin",
         dict(new_callable=PropertyMock)),
        prefix="synca.mcp.fs_extra.tool.sed")

    def has_path_arg(args):
        skip_next = False
        for arg in args:
            if skip_next:
                skip_next = False
                continue
            if arg in SedTool.flags_with_args:
                skip_next = True
                continue
            if not arg.startswith('-'):
                return True
        return False

    with patched as (m_has_path_arg, m_err_stdin):
        m_has_path_arg.side_effect = has_path_arg
        if invalid:
            with pytest.raises(FSCommandError) as e:
                tool.validate_args(args)
        else:
            assert tool.validate_args(args) is None

    if len(args) > 1 and "-f" not in args:
        assert (
            m_has_path_arg.call_args
            == [(args, ), {}])
    else:
        assert not m_has_path_arg.called
    if invalid:
        assert (
            e.value.args[0]
            == m_err_stdin.return_value)
