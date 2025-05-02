
from unittest.mock import MagicMock, PropertyMock

import pytest

from synca.mcp.python.tool.base import PythonTool
from synca.mcp.common.tool import CheckTool


def test_tool_python_constructor():
    """Test MypyTool class initialization."""
    ctx = MagicMock()
    path = MagicMock()
    tool = PythonTool(ctx, path)
    assert isinstance(tool, PythonTool)
    assert isinstance(tool, CheckTool)
    assert tool.ctx == ctx
    assert tool._path_str == path


@pytest.mark.parametrize("stdout", ["", "OUT", "a:1\nb:2"])
@pytest.mark.parametrize("stderr", ["", "ERROR"])
@pytest.mark.parametrize("return_code", [0, 1, 2])
@pytest.mark.parametrize("issues", [0, 1, 2])
def test_tool_python_parse_output(patches, return_code, stdout, stderr, issues):
    """Test parse_output method with various inputs."""
    ctx = MagicMock()
    path = MagicMock()
    tool = PythonTool(ctx, path)
    combined_output = stdout + "\n" + stderr
    message = (
        f"Issues found: {issues}"
        if issues
        else "No issues found")
    output = (
        out
        if (out := combined_output.strip())
        else "")
    patched = patches(
        "PythonTool.parse_issues",
        ("PythonTool.tool_name",
         dict(new_callable=PropertyMock)),
        prefix="synca.mcp.python.tool.base")

    with patched as (m_parse, m_tool):
        m_parse.return_value = issues
        if (return_code or 0) > 1:
            with pytest.raises(RuntimeError) as e:
                tool.parse_output(stdout, stderr, return_code)
        else:
            assert (
                tool.parse_output(stdout, stderr, return_code)
                == (return_code or 0, message, output, {}))

    if (return_code or 0) > 1:
        assert (
            str(e.value)
            == f"{m_tool.return_value} failed({return_code}): {stderr}")


@pytest.mark.parametrize("stdout", ["", "single line", "line1\nline2\nline3"])
@pytest.mark.parametrize("stderr", ["", "error message"])
def test_tool_python_parse_issues(stdout, stderr):
    """Test parse_issues method with various inputs."""
    ctx = MagicMock()
    path = MagicMock()
    tool = PythonTool(ctx, path)

    assert (
        tool.parse_issues(stdout, stderr)
        == (len(stdout.strip().splitlines())
            if stdout.strip()
            else 0))
