"""Isolated tests for synca.mcp.fs_extra.tool.grep."""

from unittest.mock import MagicMock

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


def test_grep_tool_tool_name():
    """Test the tool_name property returns the correct tool name."""
    ctx = MagicMock()
    path = MagicMock()
    args = MagicMock()
    tool = GrepTool(ctx, path, args)
    assert tool.tool_name == "grep"
    assert "tool_name" not in tool.__dict__
