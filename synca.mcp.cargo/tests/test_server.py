"""Isolated tests for synca.mcp.cargo.server."""

import inspect
from unittest.mock import MagicMock

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


@pytest.mark.parametrize("args", [[], ["ARG1", "ARG2"], None])
@pytest.mark.asyncio
async def test_cargo_clippy(patches, args):
    """Test that cargo_clippy uses the correct tool class."""
    ctx = MagicMock()
    path = MagicMock()
    test_kwargs = dict(args=args)
    kwargs = {}
    for k, v in test_kwargs.items():
        if v is not None:
            kwargs[k] = v
    patched = patches(
        "ClippyTool.run",
        prefix="synca.mcp.cargo.server")

    with patched as (m_run, ):
        assert (
            await server.cargo_clippy(ctx, path, **kwargs)
            == m_run.return_value)

    assert (
        m_run.call_args
        == [(args,), {}])


@pytest.mark.parametrize("args", [[], ["ARG1", "ARG2"], None])
@pytest.mark.asyncio
async def test_cargo_check(patches, args):
    """Test that cargo_check uses the correct tool class."""
    ctx = MagicMock()
    path = MagicMock()
    test_kwargs = dict(args=args)
    kwargs = {}
    for k, v in test_kwargs.items():
        if v is not None:
            kwargs[k] = v
    patched = patches(
        "CheckTool.run",
        prefix="synca.mcp.cargo.server")

    with patched as (m_run, ):
        assert (
            await server.cargo_check(ctx, path, **kwargs)
            == m_run.return_value)

    assert (
        m_run.call_args
        == [(args,), {}])


@pytest.mark.parametrize("args", [[], ["ARG1", "ARG2"], None])
@pytest.mark.asyncio
async def test_cargo_build(patches, args):
    """Test that cargo_build uses the correct tool class."""
    ctx = MagicMock()
    path = MagicMock()
    test_kwargs = dict(args=args)
    kwargs = {}
    for k, v in test_kwargs.items():
        if v is not None:
            kwargs[k] = v
    patched = patches(
        "BuildTool.run",
        prefix="synca.mcp.cargo.server")

    with patched as (m_run, ):
        assert (
            await server.cargo_build(ctx, path, **kwargs)
            == m_run.return_value)

    assert (
        m_run.call_args
        == [(args,), {}])


@pytest.mark.parametrize("args", [[], ["ARG1", "ARG2"], None])
@pytest.mark.asyncio
async def test_cargo_test(patches, args):
    """Test that cargo_test uses the correct tool class."""
    ctx = MagicMock()
    path = MagicMock()
    test_kwargs = dict(args=args)
    kwargs = {}
    for k, v in test_kwargs.items():
        if v is not None:
            kwargs[k] = v
    patched = patches(
        "TestTool.run",
        prefix="synca.mcp.cargo.server")

    with patched as (m_run, ):
        assert (
            await server.cargo_test(ctx, path, **kwargs)
            == m_run.return_value)

    assert (
        m_run.call_args
        == [(args,), {}])


@pytest.mark.parametrize("args", [[], ["ARG1", "ARG2"], None])
@pytest.mark.asyncio
async def test_cargo_fmt(patches, args):
    """Test that cargo_fmt uses the correct tool class."""
    ctx = MagicMock()
    path = MagicMock()
    test_kwargs = dict(args=args)
    kwargs = {}
    for k, v in test_kwargs.items():
        if v is not None:
            kwargs[k] = v
    patched = patches(
        "FmtTool.run",
        prefix="synca.mcp.cargo.server")

    with patched as (m_run, ):
        assert (
            await server.cargo_fmt(ctx, path, **kwargs)
            == m_run.return_value)

    assert (
        m_run.call_args
        == [(args,), {}])


@pytest.mark.parametrize("args", [[], ["ARG1", "ARG2"], None])
@pytest.mark.asyncio
async def test_cargo_doc(patches, args):
    """Test that cargo_doc uses the correct tool class."""
    ctx = MagicMock()
    path = MagicMock()
    test_kwargs = dict(args=args)
    kwargs = {}
    for k, v in test_kwargs.items():
        if v is not None:
            kwargs[k] = v
    patched = patches(
        "DocTool.run",
        prefix="synca.mcp.cargo.server")

    with patched as (m_run, ):
        assert (
            await server.cargo_doc(ctx, path, **kwargs)
            == m_run.return_value)

    assert (
        m_run.call_args
        == [(args,), {}])


@pytest.mark.parametrize("args", [[], ["ARG1", "ARG2"], None])
@pytest.mark.asyncio
async def test_cargo_run(patches, args):
    """Test that cargo_run uses the correct tool class."""
    ctx = MagicMock()
    path = MagicMock()
    test_kwargs = dict(args=args)
    kwargs = {}
    for k, v in test_kwargs.items():
        if v is not None:
            kwargs[k] = v
    patched = patches(
        "RunTool.run",
        prefix="synca.mcp.cargo.server")

    with patched as (m_run, ):
        assert (
            await server.cargo_run(ctx, path, **kwargs)
            == m_run.return_value)

    assert (
        m_run.call_args
        == [(args,), {}])


@pytest.mark.parametrize("args", [[], ["ARG1", "ARG2"], None])
@pytest.mark.asyncio
async def test_cargo_tarpaulin(patches, args):
    """Test that cargo_tarpaulin uses the correct tool class."""
    ctx = MagicMock()
    path = MagicMock()
    test_kwargs = dict(args=args)
    kwargs = {}
    for k, v in test_kwargs.items():
        if v is not None:
            kwargs[k] = v
    patched = patches(
        "TarpaulinTool.run",
        prefix="synca.mcp.cargo.server")

    with patched as (m_run, ):
        assert (
            await server.cargo_tarpaulin(ctx, path, **kwargs)
            == m_run.return_value)

    assert (
        m_run.call_args
        == [(args,), {}])
