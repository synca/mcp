"""Isolated tests for synca.mcp.python.server."""

import inspect
from unittest.mock import MagicMock

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
    test_kwargs = dict(pytest_args=pytest_args)
    expected = dict(
        args=pytest_args if pytest_args is not None else None)
    kwargs = {}
    for k, v in test_kwargs.items():
        if v is not None:
            kwargs[k] = v
    patched = patches(
        "PytestTool.run",
        prefix="synca.mcp.python.server")

    with patched as (m_run, ):
        assert (
            await server.pytest(ctx, path, **kwargs)
            == m_run.return_value)

    assert (
        m_run.call_args[1]
        == expected)
    assert m_run.call_args[0] == ()


@pytest.mark.parametrize("args", [[], ["ARG1", "ARG2"], None])
@pytest.mark.asyncio
async def test_tool_mypy(patches, args):
    """Test the mypy tool function to ensure it uses the right tool class."""
    ctx = MagicMock()
    path = MagicMock()
    test_kwargs = dict(mypy_args=args)
    expected = dict(
        args=args if args is not None else None)
    kwargs = {}
    for k, v in test_kwargs.items():
        if v is not None:
            kwargs[k] = v
    patched = patches(
        "MypyTool.run",
        prefix="synca.mcp.python.server")

    with patched as (m_run, ):
        assert (
            await server.mypy(ctx, path, **kwargs)
            == m_run.return_value)

    assert (
        m_run.call_args[1]
        == expected)
    assert m_run.call_args[0] == ()


@pytest.mark.parametrize("args", [[], ["ARG1", "ARG2"], None])
@pytest.mark.asyncio
async def test_tool_flake8(patches, args):
    """Test the flake8 tool function to ensure it uses the right tool class."""
    ctx = MagicMock()
    path = MagicMock()
    test_kwargs = dict(flake8_args=args)
    expected = dict(args=args)
    kwargs = {}
    for k, v in test_kwargs.items():
        if v is not None:
            kwargs[k] = v
    patched = patches(
        "Flake8Tool.run",
        prefix="synca.mcp.python.server")

    with patched as (m_run, ):
        assert (
            await server.flake8(ctx, path, **kwargs)
            == m_run.return_value)

    assert (
        m_run.call_args
        == [(), expected])
