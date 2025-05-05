
import pytest
from unittest.mock import MagicMock, PropertyMock

from synca.mcp.common.tool import HTTPTool, Tool


# HTTPTool

@pytest.mark.asyncio
async def test_http_tool_constructor():
    """Test Tool class initialization."""
    ctx = MagicMock()
    args = MagicMock()
    tool = HTTPTool(ctx, args)
    assert isinstance(tool, HTTPTool)
    assert isinstance(tool, Tool)
    assert tool.ctx == ctx
    assert tool._args == args
    with pytest.raises(NotImplementedError):
        tool.tool_name
    with pytest.raises(NotImplementedError):
        tool.request_data
    with pytest.raises(NotImplementedError):
        await tool.request(MagicMock())
    with pytest.raises(NotImplementedError):
        await tool.args


@pytest.mark.asyncio
async def test_http_tool_pipeline(patches):
    """Test pipeline method with various parameters."""
    ctx = MagicMock()
    args = MagicMock()
    tool = HTTPTool(ctx, args)
    patched = patches(
        ("HTTPTool.request_data",
         dict(new_callable=PropertyMock)),
        "HTTPTool.request",
        "HTTPTool.parse_output",
        "HTTPTool.response",
        prefix="synca.mcp.common.tool.http")

    with patched as (m_data, m_request, m_parse, m_response):
        m_request.return_value = (MagicMock(), MagicMock(), MagicMock())
        m_parse.return_value = (
            MagicMock(), MagicMock(), MagicMock(), MagicMock())
        assert (
            await tool.pipeline()
            == m_response.return_value)

    assert (
        m_request.call_args
        == [(m_data.return_value, ), {}])
    assert (
        m_parse.call_args
        == [m_request.return_value, {}])
    assert (
        m_response.call_args
        == [m_parse.return_value, {}])
