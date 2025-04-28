"""Isolated tests for synca.mcp.python.tool.mypy."""

from unittest.mock import MagicMock, PropertyMock

import pytest

from synca.mcp.common.tool import Tool
from synca.mcp.python.tool.mypy import MypyTool


def test_tool_mypy_constructor():
    """Test MypyTool class initialization."""
    ctx = MagicMock()
    path = MagicMock()
    tool = MypyTool(ctx, path)
    assert isinstance(tool, MypyTool)
    assert isinstance(tool, Tool)
    assert tool.ctx == ctx
    assert tool._path_str == path
    assert tool.tool_name == "mypy"
    assert "tool_name" not in tool.__dict__


@pytest.mark.parametrize("stdout", ["MYPY INFO", "OUT", "a:1\nb:2"])
@pytest.mark.parametrize("stderr", ["", "ERROR"])
@pytest.mark.parametrize("returncode", [None, 0, 1, 2])
def test_tool_mypy_parse_output(patches, returncode, stdout, stderr):
    """Test mypy.parse_output method with various inputs."""
    ctx = MagicMock()
    path = MagicMock()
    tool = MypyTool(ctx, path)
    combined_output = stdout + "\n" + stderr
    stdout_length = len(stdout.strip().splitlines())
    issues_count = (stdout_length - 1) if stdout.strip() else 0
    msg_output = (
        combined_output.strip()
        if issues_count
        else "No issues found")
    patched = patches(
        ("MypyTool.tool_name",
         dict(new_callable=PropertyMock)),
        prefix="synca.mcp.python.tool.mypy")

    with patched as (m_tool, ):
        if (returncode or 0) > 1:
            with pytest.raises(RuntimeError) as e:
                tool.parse_output(stdout, stderr, returncode)
        else:
            assert (
                tool.parse_output(stdout, stderr, returncode)
                == (returncode or 0, issues_count, msg_output, {}))

    if (returncode or 0) > 1:
        assert (
            str(e.value)
            == f"{m_tool.return_value} failed: {stderr}")
