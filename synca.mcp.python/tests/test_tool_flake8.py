"""Isolated tests for synca.mcp.python.tool.flake8."""

from unittest.mock import MagicMock

from synca.mcp.python.tool.base import PythonTool
from synca.mcp.python.tool.flake8 import Flake8Tool


def test_tool_flake8_constructor():
    """Test Flake8Tool class initialization."""
    ctx = MagicMock()
    path = MagicMock()
    tool = Flake8Tool(ctx, path)
    assert isinstance(tool, Flake8Tool)
    assert isinstance(tool, PythonTool)
    assert tool.ctx == ctx
    assert tool._path_str == path
    assert tool.tool_name == "flake8"
    assert "tool_name" not in tool.__dict__
