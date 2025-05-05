"""Isolated tests for synca.mcp.common.tool."""

import pytest
from unittest.mock import MagicMock

from synca.mcp.common.tool import Tool


@pytest.mark.asyncio
async def test_tool_constructor():
    """Test Tool class initialization."""
    ctx = MagicMock()
    tool = Tool(ctx)
    assert tool.ctx == ctx
    with pytest.raises(NotImplementedError):
        tool.tool_name
    with pytest.raises(NotImplementedError):
        await tool.parse_output(
            MagicMock(),
            MagicMock(),
            MagicMock())
    with pytest.raises(NotImplementedError):
        await tool.pipeline()


def test_tool_parse_output(patches):
    """Test parse_output method."""
    ctx = MagicMock()
    tool = Tool(ctx)
    with pytest.raises(NotImplementedError):
        tool.parse_output(
            MagicMock(), MagicMock(), MagicMock())


def test_tool_response(patches):
    """Test response method with parametrized inputs."""
    ctx = MagicMock()
    output = MagicMock()
    tool = Tool(ctx)
    info = MagicMock()
    return_code = MagicMock()
    message = MagicMock()
    assert (
        tool.response(return_code, message, output, info)
        == {
            "data": {
                "return_code": return_code,
                "message": message,
                "output": output,
                "info": info,
            }})


@pytest.mark.parametrize(
    "error",
    [None,
     BaseException])
@pytest.mark.asyncio
async def test_tool_run(patches, iters, error):
    """Test run() with parametrized arguments."""
    ctx = MagicMock()
    tool = Tool(ctx)
    tool.__class__.__name__ = "CustomTool"
    patched = patches(
        "traceback",
        "Tool.pipeline",
        prefix="synca.mcp.common.tool.base")

    with patched as (m_tb, m_pipeline):
        if error:
            m_pipeline.side_effect = error("Test error")
        assert (
            await tool.run()
            == (m_pipeline.return_value
                if not error
                else dict(
                    error=(
                        "Failed to run custom: Test error\n"
                        f"{m_tb.format_exc.return_value}"))))

    assert (
        m_pipeline.call_args
        == [(), {}])
    if error:
        assert (
            m_tb.format_exc.call_args
            == [(), {}])
        return
    assert not m_tb.format_exc.called
