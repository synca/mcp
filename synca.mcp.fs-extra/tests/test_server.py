"""Isolated tests for synca.mcp.fs_extra.server."""

import inspect
from unittest.mock import MagicMock

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
    "args",
    [None, [], ["ARG1", "ARG2"], ["-n", "10", "file.txt"]])
@pytest.mark.asyncio
async def test_fs_head(
        patches,
        args):
    """Test the fs_head tool function to ensure it uses the right tool class."""
    ctx = MagicMock()
    path = MagicMock()
    test_kwargs = dict(args=args)
    kwargs = {}
    for k, v in test_kwargs.items():
        if v is not None:
            kwargs[k] = v
    patched = patches(
        "HeadTool.__init__",
        "HeadTool.run",
        prefix="synca.mcp.fs_extra.server")

    with patched as (m_init, m_run):
        m_init.return_value = None
        assert (
            await server.fs_head(ctx, path, **kwargs)
            == m_run.return_value)

    assert (
        m_init.call_args
        == [(ctx, path, args), {}])
    assert (
        m_run.call_args
        == [(), {}])


@pytest.mark.parametrize(
    "args",
    [None, [], ["ARG1", "ARG2"], ["-n", "10", "file.txt"]])
@pytest.mark.asyncio
async def test_fs_tail(
        patches,
        args):
    """Test the fs_tail tool function to ensure it uses the right tool class."""
    ctx = MagicMock()
    path = MagicMock()
    test_kwargs = dict(args=args)
    kwargs = {}
    for k, v in test_kwargs.items():
        if v is not None:
            kwargs[k] = v
    patched = patches(
        "TailTool.__init__",
        "TailTool.run",
        prefix="synca.mcp.fs_extra.server")

    with patched as (m_init, m_run):
        m_init.return_value = None
        assert (
            await server.fs_tail(ctx, path, **kwargs)
            == m_run.return_value)

    assert (
        m_init.call_args
        == [(ctx, path, args), {}])
    assert (
        m_run.call_args
        == [(), {}])


@pytest.mark.parametrize("args", [
    [],
    ["ARG1", "ARG2"],
    ["pattern", "file.txt"],
    ["-i", "file.txt"]
])
@pytest.mark.asyncio
async def test_fs_grep(
        patches,
        args):
    """Test the fs_grep tool function to ensure it uses the right tool class."""
    ctx = MagicMock()
    path = MagicMock()
    test_kwargs = dict(args=args)
    kwargs = {}
    for k, v in test_kwargs.items():
        if v is not None:
            kwargs[k] = v
    patched = patches(
        "GrepTool.__init__",
        "GrepTool.run",
        prefix="synca.mcp.fs_extra.server")

    with patched as (m_init, m_run):
        m_init.return_value = None
        assert (
            await server.fs_grep(ctx, path, **kwargs)
            == m_run.return_value)

    assert (
        m_init.call_args
        == [(ctx, path, args), {}])
    assert (
        m_run.call_args
        == [(), {}])


@pytest.mark.parametrize("args", [
    None,
    [],
    ["ARG1", "ARG2"],
    ["s/old/new/g", "file.txt"]
])
@pytest.mark.asyncio
async def test_fs_sed(
        patches,
        args):
    """Test the fs_sed tool function to ensure it uses the right tool class."""
    ctx = MagicMock()
    path = MagicMock()
    test_kwargs = dict(args=args)
    kwargs = {}
    for k, v in test_kwargs.items():
        if v is not None:
            kwargs[k] = v
    patched = patches(
        "SedTool.__init__",
        "SedTool.run",
        prefix="synca.mcp.fs_extra.server")

    with patched as (m_init, m_run):
        m_init.return_value = None
        assert (
            await server.fs_sed(ctx, path, **kwargs)
            == m_run.return_value)

    assert (
        m_init.call_args
        == [(ctx, path, args), {}])
    assert (
        m_run.call_args
        == [(), {}])
