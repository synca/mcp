"""Isolated tests for synca.mcp.python.tool.mypy."""

from unittest.mock import MagicMock

import pytest

from synca.mcp.python.tool.base import PythonTool
from synca.mcp.python.tool.mypy import MypyTool


def test_tool_mypy_constructor():
    """Test MypyTool class initialization."""
    ctx = MagicMock()
    path = MagicMock()
    args = MagicMock()
    tool = MypyTool(ctx, path, args)
    assert isinstance(tool, MypyTool)
    assert isinstance(tool, PythonTool)
    assert tool.ctx == ctx
    assert tool._path_str == path
    assert tool.tool_name == "mypy"
    assert "tool_name" not in tool.__dict__
    assert tool._args == args


@pytest.mark.parametrize("stdout", ["", "single line", "line1\nline2\nline3"])
@pytest.mark.parametrize("stderr", ["", "error message"])
def test_tool_mypy_parse_issues(stdout, stderr):
    """Test parse_issues method with various inputs."""
    ctx = MagicMock()
    path = MagicMock()
    args = MagicMock()
    tool = MypyTool(ctx, path, args)

    assert (
        tool.parse_issues(stdout, stderr)
        == ((len(stdout.strip().splitlines()) - 1)
            if stdout.strip()
            else 0))
