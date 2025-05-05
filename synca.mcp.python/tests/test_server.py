"""Isolated tests for synca.mcp.python.server."""

import inspect
from unittest.mock import AsyncMock, MagicMock

import pytest
from mcp.server.fastmcp import FastMCP

from synca.mcp.python import server


def test_fastmcp_initialization():
    """Test the FastMCP initialization in server.py."""
    assert isinstance(server.mcp, FastMCP)
    assert server.mcp.name == "Python"
    assert (
        set(["pytest", "flake8", "mypy"])
        <= set(f[0] for f in inspect.getmembers(server, inspect.isfunction)))


@pytest.mark.parametrize("pytest_args", [[], ["ARG1", "ARG2"], None])
@pytest.mark.asyncio
async def test_tool_pytest(
        patches,
        pytest_args):
    """Test each tool function to ensure it uses the right tool class."""
    ctx = MagicMock()
    path = MagicMock()
    kwargs = (
        dict(pytest_args=pytest_args)
        if pytest_args is not None
        else {})
    expected = dict(args=pytest_args)
    mock_run = AsyncMock()
    patched = patches(
        "PytestTool",
        prefix="synca.mcp.python.server")

    with patched as (m_tool, ):
        m_tool.return_value.run = mock_run
        assert (
            await server.pytest(ctx, path, **kwargs)
            == m_tool.return_value.run.return_value)

    assert (
        m_tool.call_args
        == [(ctx, path, expected), {}])
    assert (
        mock_run.call_args
        == [(), {}])


@pytest.mark.parametrize("mypy_args", [[], ["ARG1", "ARG2"], None])
@pytest.mark.asyncio
async def test_tool_mypy(patches, mypy_args):
    """Test the mypy tool function to ensure it uses the right tool class."""
    ctx = MagicMock()
    path = MagicMock()
    kwargs = (
        dict(mypy_args=mypy_args)
        if mypy_args is not None
        else {})
    expected = dict(args=mypy_args)
    mock_run = AsyncMock()
    patched = patches(
        "MypyTool",
        prefix="synca.mcp.python.server")

    with patched as (m_tool, ):
        m_tool.return_value.run = mock_run
        assert (
            await server.mypy(ctx, path, **kwargs)
            == m_tool.return_value.run.return_value)

    assert (
        m_tool.call_args
        == [(ctx, path, expected), {}])
    assert (
        mock_run.call_args
        == [(), {}])


@pytest.mark.parametrize("flake8_args", [[], ["ARG1", "ARG2"], None])
@pytest.mark.asyncio
async def test_tool_flake8(patches, flake8_args):
    """Test the flake8 tool function to ensure it uses the right tool class."""
    ctx = MagicMock()
    path = MagicMock()
    kwargs = (
        dict(flake8_args=flake8_args)
        if flake8_args is not None
        else {})
    expected = dict(args=flake8_args)
    mock_run = AsyncMock()
    patched = patches(
        "Flake8Tool",
        prefix="synca.mcp.python.server")

    with patched as (m_tool, ):
        m_tool.return_value.run = mock_run
        assert (
            await server.flake8(ctx, path, **kwargs)
            == m_tool.return_value.run.return_value)

    assert (
        m_tool.call_args
        == [(ctx, path, expected), {}])
    assert (
        mock_run.call_args
        == [(), {}])
