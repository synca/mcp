"""Isolated tests for synca.mcp.gh_extra.server.workflow."""

from unittest.mock import AsyncMock, MagicMock

import pytest

from synca.mcp.gh_extra import server


@pytest.mark.asyncio
async def test_list_workflow_runs(patches):
    """Test that list_workflow_runs uses the correct tool class."""
    ctx = MagicMock()
    owner = MagicMock()
    repo = MagicMock()
    actor = MagicMock()
    branch = MagicMock()
    event = MagicMock()
    status = MagicMock()
    per_page = MagicMock()
    page = MagicMock()
    created = MagicMock()
    workflow_id = MagicMock()
    exclude_pull_requests = MagicMock()
    check_suite_id = MagicMock()
    head_sha = MagicMock()
    jq = MagicMock()
    expected = dict(
        owner=owner,
        repo=repo,
        actor=actor,
        branch=branch,
        event=event,
        status=status,
        per_page=per_page,
        page=page,
        created=created,
        workflow_id=workflow_id,
        exclude_pull_requests=exclude_pull_requests,
        check_suite_id=check_suite_id,
        head_sha=head_sha,
        jq=jq)
    mock_run = AsyncMock()
    patched = patches(
        "WorkflowRunsTool",
        prefix="synca.mcp.gh_extra.server.workflow")

    with patched as (m_tool, ):
        m_tool.return_value.run = mock_run
        assert (
            await server.list_workflow_runs(
                ctx=ctx,
                owner=owner,
                repo=repo,
                actor=actor,
                branch=branch,
                event=event,
                status=status,
                per_page=per_page,
                page=page,
                created=created,
                workflow_id=workflow_id,
                exclude_pull_requests=exclude_pull_requests,
                check_suite_id=check_suite_id,
                head_sha=head_sha,
                jq=jq)
            == m_tool.return_value.run.return_value)

    assert (
        m_tool.call_args
        == [(ctx, expected), {}])
    assert (
        mock_run.call_args
        == [(), {}])


@pytest.mark.asyncio
async def test_get_workflow_run(patches):
    """Test that get_workflow_run uses the correct tool class."""
    ctx = MagicMock()
    owner = MagicMock()
    repo = MagicMock()
    run_id = MagicMock()
    exclude_pull_requests = MagicMock()
    expected = dict(
        owner=owner,
        repo=repo,
        run_id=run_id,
        exclude_pull_requests=exclude_pull_requests)
    mock_run = AsyncMock()
    patched = patches(
        "WorkflowRunsTool",
        prefix="synca.mcp.gh_extra.server.workflow")

    with patched as (m_tool, ):
        m_tool.return_value.run = mock_run
        assert (
            await server.get_workflow_run(
                ctx=ctx,
                owner=owner,
                repo=repo,
                run_id=run_id,
                exclude_pull_requests=exclude_pull_requests)
            == m_tool.return_value.run.return_value)

    assert (
        m_tool.call_args
        == [(ctx, expected), {}])
    assert (
        mock_run.call_args
        == [(), {}])


@pytest.mark.asyncio
async def test_get_workflow_logs(patches):
    """Test that get_workflow_logs uses the correct tool class."""
    ctx = MagicMock()
    owner = MagicMock()
    repo = MagicMock()
    run_id = MagicMock()
    expected = dict(
        owner=owner,
        repo=repo,
        run_id=run_id)
    mock_run = AsyncMock()
    patched = patches(
        "WorkflowLogsTool",
        prefix="synca.mcp.gh_extra.server.workflow")

    with patched as (m_tool, ):
        m_tool.return_value.run = mock_run
        assert (
            await server.get_workflow_logs(
                ctx=ctx,
                owner=owner,
                repo=repo,
                run_id=run_id)
            == m_tool.return_value.run.return_value)

    assert (
        m_tool.call_args
        == [(ctx, expected), {}])
    assert (
        mock_run.call_args
        == [(), {}])
