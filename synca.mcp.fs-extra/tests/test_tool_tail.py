"""Isolated tests for synca.mcp.fs_extra.tool.tail."""

from unittest.mock import MagicMock

from synca.mcp.fs_extra.tool.base import UnixSliceTool
from synca.mcp.fs_extra.tool.tail import TailTool


def test_tail_tool_constructor():
    """Test TailTool class initialization."""
    ctx = MagicMock()
    path = MagicMock()
    args = MagicMock()
    tool = TailTool(ctx, path, args)
    assert isinstance(tool, UnixSliceTool)
    assert tool.ctx == ctx
    assert tool._path_str == path
    assert tool.args == args
    assert tool.success_message == "Successfully read the end of file"


def test_tail_tool_tool_name():
    """Test the tool_name property returns the correct tool name."""
    ctx = MagicMock()
    path = MagicMock()
    args = MagicMock()
    tool = TailTool(ctx, path, args)
    assert tool.tool_name == "tail"
    assert "tool_name" not in tool.__dict__
