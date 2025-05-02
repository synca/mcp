"""Isolated tests for synca.mcp.gh_extra.server.check."""

from unittest.mock import AsyncMock, MagicMock

import pytest

from synca.mcp.gh_extra import server


@pytest.mark.asyncio
async def test_list_check_runs_for_check_suite(patches):
    """Test that list_check_runs_for_check_suite uses the correct tool class.

    Verifies proper tool class instantiation and parameter passing.
    """
    ctx = MagicMock()
    owner = MagicMock()
    repo = MagicMock()
    check_suite_id = MagicMock()
    status = MagicMock()
    check_name = MagicMock()
    filter = MagicMock()
    per_page = MagicMock()
    page = MagicMock()
    jq = MagicMock()
    expected = dict(
        owner=owner,
        repo=repo,
        check_suite_id=check_suite_id,
        status=status,
        check_name=check_name,
        filter=filter,
        per_page=per_page,
        page=page,
        jq=jq)
    mock_run = AsyncMock()
    patched = patches(
        "CheckRunsForSuiteTool",
        prefix="synca.mcp.gh_extra.server.check")

    with patched as (m_tool, ):
        m_tool.return_value.run = mock_run
        assert (
            await server.list_check_runs_for_check_suite(
                ctx=ctx,
                owner=owner,
                repo=repo,
                check_suite_id=check_suite_id,
                status=status,
                check_name=check_name,
                filter=filter,
                per_page=per_page,
                page=page,
                jq=jq)
            == m_tool.return_value.run.return_value)

    assert (
        m_tool.call_args
        == [(ctx, expected), {}])
    assert (
        mock_run.call_args
        == [(), {}])


@pytest.mark.asyncio
async def test_list_check_runs_for_ref(patches):
    """Test that list_check_runs_for_ref uses the correct tool class.

    Verifies proper tool class instantiation and parameter passing.
    """
    ctx = MagicMock()
    owner = MagicMock()
    repo = MagicMock()
    ref = MagicMock()
    check_name = MagicMock()
    status = MagicMock()
    filter = MagicMock()
    per_page = MagicMock()
    page = MagicMock()
    app_id = MagicMock()
    jq = MagicMock()
    expected = dict(
        owner=owner,
        repo=repo,
        ref=ref,
        check_name=check_name,
        status=status,
        filter=filter,
        per_page=per_page,
        page=page,
        app_id=app_id,
        jq=jq)
    mock_run = AsyncMock()
    patched = patches(
        "CheckRunsTool",
        prefix="synca.mcp.gh_extra.server.check")

    with patched as (m_tool, ):
        m_tool.return_value.run = mock_run
        assert (
            await server.list_check_runs_for_ref(
                ctx=ctx,
                owner=owner,
                repo=repo,
                ref=ref,
                check_name=check_name,
                status=status,
                filter=filter,
                per_page=per_page,
                page=page,
                app_id=app_id,
                jq=jq)
            == m_tool.return_value.run.return_value)

    assert (
        m_tool.call_args
        == [(ctx, expected), {}])
    assert (
        mock_run.call_args
        == [(), {}])


@pytest.mark.asyncio
async def test_list_check_suites_for_ref(patches):
    """Test that list_check_suites_for_ref uses the correct tool class.

    Verifies proper tool class instantiation and parameter passing.
    """
    ctx = MagicMock()
    owner = MagicMock()
    repo = MagicMock()
    ref = MagicMock()
    app_id = MagicMock()
    check_name = MagicMock()
    per_page = MagicMock()
    page = MagicMock()
    jq = MagicMock()
    expected = dict(
        owner=owner,
        repo=repo,
        ref=ref,
        app_id=app_id,
        check_name=check_name,
        per_page=per_page,
        page=page,
        jq=jq)
    mock_run = AsyncMock()
    patched = patches(
        "CheckSuitesTool",
        prefix="synca.mcp.gh_extra.server.check")

    with patched as (m_tool, ):
        m_tool.return_value.run = mock_run
        assert (
            await server.list_check_suites_for_ref(
                ctx=ctx,
                owner=owner,
                repo=repo,
                ref=ref,
                app_id=app_id,
                check_name=check_name,
                per_page=per_page,
                page=page,
                jq=jq)
            == m_tool.return_value.run.return_value)

    assert (
        m_tool.call_args
        == [(ctx, expected), {}])
    assert (
        mock_run.call_args
        == [(), {}])
