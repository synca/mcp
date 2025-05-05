"""Isolated tests for synca.mcp.fs_extra.tool.head."""

from unittest.mock import MagicMock

from synca.mcp.fs_extra.tool.base import UnixSliceTool
from synca.mcp.fs_extra.tool.head import HeadTool


def test_head_tool_constructor():
    """Test HeadTool class initialization."""
    ctx = MagicMock()
    path = MagicMock()
    args = MagicMock()
    tool = HeadTool(ctx, path, args)
    assert isinstance(tool, UnixSliceTool)
    assert tool.ctx == ctx
    assert tool._path_str == path
    assert tool._args == args
    assert tool.success_message == "Successfully read the beginning of file"


def test_head_tool_tool_name():
    """Test the tool_name property returns the correct tool name."""
    ctx = MagicMock()
    path = MagicMock()
    args = MagicMock()
    tool = HeadTool(ctx, path, args)
    assert tool.tool_name == "head"
    assert "tool_name" not in tool.__dict__
