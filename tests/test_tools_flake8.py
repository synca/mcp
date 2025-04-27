"""Isolated tests for snake.mcp.server.tools.flake8."""

from unittest.mock import MagicMock, PropertyMock

import pytest

from snake.mcp.server.tools.base import Tool
from snake.mcp.server.tools.flake8 import Flake8Tool


def test_tools_flake8_constructor():
    """Test Flake8Tool class initialization."""
    ctx = MagicMock()
    path = MagicMock()
    tool = Flake8Tool(ctx, path)
    assert isinstance(tool, Flake8Tool)
    assert isinstance(tool, Tool)
    assert tool.ctx == ctx
    assert tool._path_str == path
    assert tool.tool_name == "flake8"
    assert "tool_name" not in tool.__dict__


@pytest.mark.parametrize("stdout", ["", "OUT", "a:1\nb:2"])
@pytest.mark.parametrize("stderr", ["", "ERROR"])
@pytest.mark.parametrize("returncode", [None, 0, 1, 2])
def test_tools_flake8_parse_output(patches, returncode, stdout, stderr):
    """Test flake8.parse_output method with various inputs."""
    ctx = MagicMock()
    path = MagicMock()
    tool = Flake8Tool(ctx, path)
    combined_output = stdout + "\n" + stderr
    stdout_length = len(stdout.strip().splitlines())
    issues_count = stdout_length if stdout.strip() else 0
    msg_output = (
        out
        if (out := combined_output.strip())
        else "No issues found")
    patched = patches(
        ("Flake8Tool.tool_name",
         dict(new_callable=PropertyMock)),
        prefix="snake.mcp.server.tools.flake8")

    with patched as (m_tool, ):
        if (returncode or 0) > 1:
            with pytest.raises(RuntimeError) as e:
                tool.parse_output(stdout, stderr, returncode)
        else:
            assert (
                tool.parse_output(stdout, stderr, returncode)
                == (issues_count, msg_output, {}))

    if (returncode or 0) > 1:
        assert (
            str(e.value)
            == f"{m_tool.return_value} failed: {stderr}")
