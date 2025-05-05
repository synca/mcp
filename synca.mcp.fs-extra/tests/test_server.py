"""Isolated tests for synca.mcp.fs_extra.server."""

import inspect
from unittest.mock import AsyncMock, MagicMock

import pytest
from mcp.server.fastmcp import FastMCP

from synca.mcp.fs_extra import server


def test_fastmcp_initialization():
    """Test the FastMCP initialization in server.py."""
    assert isinstance(server.mcp, FastMCP)
    assert server.mcp.name == "FS-Extra"
    assert (
        set(["fs_head", "fs_tail", "fs_grep", "fs_sed"])
        <= set(f[0] for f in inspect.getmembers(server, inspect.isfunction)))


@pytest.mark.parametrize(
    "head_args",
    [[], ["ARG1", "ARG2"], ["-n", "10", "file.txt"]])
@pytest.mark.asyncio
async def test_fs_head(patches, head_args):
    """Test the fs_head tool function to ensure it uses the right tool class."""
    ctx = MagicMock()
    path = MagicMock()
    kwargs = dict(head_args=head_args)
    expected = dict(args=head_args)
    mock_run = AsyncMock()
    patched = patches(
        "HeadTool",
        prefix="synca.mcp.fs_extra.server")

    with patched as (m_tool, ):
        m_tool.return_value.run = mock_run
        assert (
            await server.fs_head(ctx, path, **kwargs)
            == m_tool.return_value.run.return_value)

    assert (
        m_tool.call_args
        == [(ctx, path, expected), {}])
    assert (
        mock_run.call_args
        == [(), {}])


@pytest.mark.parametrize(
    "tail_args",
    [[], ["ARG1", "ARG2"], ["-n", "10", "file.txt"]])
@pytest.mark.asyncio
async def test_fs_tail(patches, tail_args):
    """Test the fs_tail tool function to ensure it uses the right tool class."""
    ctx = MagicMock()
    path = MagicMock()
    kwargs = dict(tail_args=tail_args)
    expected = dict(args=tail_args)
    mock_run = AsyncMock()
    patched = patches(
        "TailTool",
        prefix="synca.mcp.fs_extra.server")

    with patched as (m_tool, ):
        m_tool.return_value.run = mock_run
        assert (
            await server.fs_tail(ctx, path, **kwargs)
            == m_tool.return_value.run.return_value)

    assert (
        m_tool.call_args
        == [(ctx, path, expected), {}])
    assert (
        mock_run.call_args
        == [(), {}])


@pytest.mark.parametrize(
    "grep_args",
    [[],
     ["ARG1", "ARG2"],
     ["s/old/new/g", "file.txt"]])
@pytest.mark.asyncio
async def test_fs_grep(patches, grep_args):
    """Test the fs_grep tool function to ensure it uses the right tool class."""
    ctx = MagicMock()
    path = MagicMock()
    kwargs = dict(grep_args=grep_args)
    expected = dict(args=grep_args)
    mock_run = AsyncMock()
    patched = patches(
        "GrepTool",
        prefix="synca.mcp.fs_extra.server")

    with patched as (m_tool, ):
        m_tool.return_value.run = mock_run
        assert (
            await server.fs_grep(ctx, path, **kwargs)
            == m_tool.return_value.run.return_value)

    assert (
        m_tool.call_args
        == [(ctx, path, expected), {}])
    assert (
        mock_run.call_args
        == [(), {}])


@pytest.mark.parametrize(
    "sed_args",
    [[],
     ["ARG1", "ARG2"],
     ["s/old/new/g", "file.txt"]])
@pytest.mark.asyncio
async def test_fs_sed(patches, sed_args):
    """Test the fs_sed tool function to ensure it uses the right tool class."""
    ctx = MagicMock()
    path = MagicMock()
    kwargs = dict(sed_args=sed_args)
    expected = dict(args=sed_args)
    mock_run = AsyncMock()
    patched = patches(
        "SedTool",
        prefix="synca.mcp.fs_extra.server")

    with patched as (m_tool, ):
        m_tool.return_value.run = mock_run
        assert (
            await server.fs_sed(ctx, path, **kwargs)
            == m_tool.return_value.run.return_value)

    assert (
        m_tool.call_args
        == [(ctx, path, expected), {}])
    assert (
        mock_run.call_args
        == [(), {}])
