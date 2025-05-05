"""Isolated tests for synca.mcp.cargo.server."""

import inspect
from unittest.mock import AsyncMock, MagicMock

import pytest
from mcp.server.fastmcp import FastMCP

from synca.mcp.cargo import server


def test_fastmcp_initialization():
    """Test the FastMCP initialization in server.py."""
    assert isinstance(server.mcp, FastMCP)
    assert server.mcp.name == "Cargo"
    assert (
        set(["cargo_clippy", "cargo_check", "cargo_build", "cargo_test",
             "cargo_fmt", "cargo_doc", "cargo_run", "cargo_tarpaulin"])
        <= set(f[0] for f in inspect.getmembers(server, inspect.isfunction)))


@pytest.mark.parametrize("clippy_args", [[], ["ARG1", "ARG2"], None])
@pytest.mark.asyncio
async def test_cargo_clippy(patches, clippy_args):
    """Test that cargo_clippy uses the correct tool class."""
    ctx = MagicMock()
    path = MagicMock()
    kwargs = (
        dict(clippy_args=clippy_args)
        if clippy_args is not None
        else {})
    expected = dict(args=clippy_args)
    mock_run = AsyncMock()
    patched = patches(
        "ClippyTool",
        prefix="synca.mcp.cargo.server")

    with patched as (m_tool, ):
        m_tool.return_value.run = mock_run
        assert (
            await server.cargo_clippy(ctx, path, **kwargs)
            == m_tool.return_value.run.return_value)

    assert (
        m_tool.call_args
        == [(ctx, path, expected), {}])
    assert (
        mock_run.call_args
        == [(), {}])


@pytest.mark.parametrize("check_args", [[], ["ARG1", "ARG2"], None])
@pytest.mark.asyncio
async def test_cargo_check(patches, check_args):
    """Test that cargo_check uses the correct tool class."""
    ctx = MagicMock()
    path = MagicMock()
    kwargs = (
        dict(check_args=check_args)
        if check_args is not None
        else {})
    expected = dict(args=check_args)
    mock_run = AsyncMock()
    patched = patches(
        "CheckTool",
        prefix="synca.mcp.cargo.server")

    with patched as (m_tool, ):
        m_tool.return_value.run = mock_run
        assert (
            await server.cargo_check(ctx, path, **kwargs)
            == m_tool.return_value.run.return_value)

    assert (
        m_tool.call_args
        == [(ctx, path, expected), {}])
    assert (
        mock_run.call_args
        == [(), {}])


@pytest.mark.parametrize("build_args", [[], ["ARG1", "ARG2"], None])
@pytest.mark.asyncio
async def test_cargo_build(patches, build_args):
    """Test that cargo_build uses the correct tool class."""
    ctx = MagicMock()
    path = MagicMock()
    kwargs = (
        dict(build_args=build_args)
        if build_args is not None
        else {})
    expected = dict(args=build_args)
    mock_run = AsyncMock()
    patched = patches(
        "BuildTool",
        prefix="synca.mcp.cargo.server")

    with patched as (m_tool, ):
        m_tool.return_value.run = mock_run
        assert (
            await server.cargo_build(ctx, path, **kwargs)
            == m_tool.return_value.run.return_value)

    assert (
        m_tool.call_args
        == [(ctx, path, expected), {}])
    assert (
        mock_run.call_args
        == [(), {}])


@pytest.mark.parametrize("test_args", [[], ["ARG1", "ARG2"], None])
@pytest.mark.asyncio
async def test_cargo_test(patches, test_args):
    """Test that cargo_test uses the correct tool class."""
    ctx = MagicMock()
    path = MagicMock()
    kwargs = (
        dict(test_args=test_args)
        if test_args is not None
        else {})
    expected = dict(args=test_args)
    mock_run = AsyncMock()
    patched = patches(
        "TestTool",
        prefix="synca.mcp.cargo.server")

    with patched as (m_tool, ):
        m_tool.return_value.run = mock_run
        assert (
            await server.cargo_test(ctx, path, **kwargs)
            == m_tool.return_value.run.return_value)

    assert (
        m_tool.call_args
        == [(ctx, path, expected), {}])
    assert (
        mock_run.call_args
        == [(), {}])


@pytest.mark.parametrize("fmt_args", [[], ["ARG1", "ARG2"], None])
@pytest.mark.asyncio
async def test_cargo_fmt(patches, fmt_args):
    """Test that cargo_fmt uses the correct tool class."""
    ctx = MagicMock()
    path = MagicMock()
    kwargs = (
        dict(fmt_args=fmt_args)
        if fmt_args is not None
        else {})
    expected = dict(args=fmt_args)
    mock_run = AsyncMock()
    patched = patches(
        "FmtTool",
        prefix="synca.mcp.cargo.server")

    with patched as (m_tool, ):
        m_tool.return_value.run = mock_run
        assert (
            await server.cargo_fmt(ctx, path, **kwargs)
            == m_tool.return_value.run.return_value)

    assert (
        m_tool.call_args
        == [(ctx, path, expected), {}])
    assert (
        mock_run.call_args
        == [(), {}])


@pytest.mark.parametrize("doc_args", [[], ["ARG1", "ARG2"], None])
@pytest.mark.asyncio
async def test_cargo_doc(patches, doc_args):
    """Test that cargo_doc uses the correct tool class."""
    ctx = MagicMock()
    path = MagicMock()
    kwargs = (
        dict(doc_args=doc_args)
        if doc_args is not None
        else {})
    expected = dict(args=doc_args)
    mock_run = AsyncMock()
    patched = patches(
        "DocTool",
        prefix="synca.mcp.cargo.server")

    with patched as (m_tool, ):
        m_tool.return_value.run = mock_run
        assert (
            await server.cargo_doc(ctx, path, **kwargs)
            == m_tool.return_value.run.return_value)

    assert (
        m_tool.call_args
        == [(ctx, path, expected), {}])
    assert (
        mock_run.call_args
        == [(), {}])


@pytest.mark.parametrize("run_args", [[], ["ARG1", "ARG2"], None])
@pytest.mark.asyncio
async def test_cargo_run(patches, run_args):
    """Test that cargo_run uses the correct tool class."""
    ctx = MagicMock()
    path = MagicMock()
    kwargs = (
        dict(run_args=run_args)
        if run_args is not None
        else {})
    expected = dict(args=run_args)
    mock_run = AsyncMock()
    patched = patches(
        "RunTool",
        prefix="synca.mcp.cargo.server")

    with patched as (m_tool, ):
        m_tool.return_value.run = mock_run
        assert (
            await server.cargo_run(ctx, path, **kwargs)
            == m_tool.return_value.run.return_value)

    assert (
        m_tool.call_args
        == [(ctx, path, expected), {}])
    assert (
        mock_run.call_args
        == [(), {}])


@pytest.mark.parametrize("tarpaulin_args", [[], ["ARG1", "ARG2"], None])
@pytest.mark.asyncio
async def test_cargo_tarpaulin(patches, tarpaulin_args):
    """Test that cargo_tarpaulin uses the correct tool class."""
    ctx = MagicMock()
    path = MagicMock()
    kwargs = (
        dict(tarpaulin_args=tarpaulin_args)
        if tarpaulin_args is not None
        else {})
    expected = dict(args=tarpaulin_args)
    mock_run = AsyncMock()
    patched = patches(
        "TarpaulinTool",
        prefix="synca.mcp.cargo.server")

    with patched as (m_tool, ):
        m_tool.return_value.run = mock_run
        assert (
            await server.cargo_tarpaulin(ctx, path, **kwargs)
            == m_tool.return_value.run.return_value)

    assert (
        m_tool.call_args
        == [(ctx, path, expected), {}])
    assert (
        mock_run.call_args
        == [(), {}])
