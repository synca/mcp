"""Isolated tests for synca.mcp.fs_extra.tool.sed."""

from unittest.mock import MagicMock

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
    assert tool.args == args
    assert tool.success_message == "Successfully ran the sed command"


def test_sed_tool_tool_name():
    """Test the tool_name property returns the correct tool name."""
    ctx = MagicMock()
    path = MagicMock()
    args = MagicMock()
    tool = SedTool(ctx, path, args)
    assert tool.tool_name == "sed"
    assert "tool_name" not in tool.__dict__
