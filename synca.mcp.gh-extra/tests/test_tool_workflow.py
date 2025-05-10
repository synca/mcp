"""Isolated tests for synca.mcp.gh_extra.tool.workflow."""

from unittest.mock import MagicMock, PropertyMock

import pytest

from synca.mcp.gh_extra.tool import workflow


def test_workflow_runs_tool_constructor():
    """Test the WorkflowRunsTool constructor."""
    ctx = MagicMock()
    args = {"key": MagicMock()}
    tool = workflow.WorkflowRunsTool(ctx, args)
    assert tool.ctx is ctx
    assert tool._args is args
    assert tool._endpoint_run == "/repos/{owner}/{repo}/actions/runs/{run_id}"
    assert tool._endpoint_runs == "/repos/{owner}/{repo}/actions/runs"
    assert tool._api_method_run == "getitem"
    assert tool._api_method_runs == "getitems"
    assert tool.iterable_key == "workflow_runs"


@pytest.mark.parametrize("has_run_id", [True, False])
def test_workflow_runs_tool_api_method(patches, has_run_id):
    """Test the WorkflowRunsTool api_method property."""
    ctx = MagicMock()
    args = MagicMock()
    tool = workflow.WorkflowRunsTool(ctx, args)
    patched = patches(
        ("WorkflowRunsTool.args",
         dict(new_callable=PropertyMock)),
        prefix="synca.mcp.gh_extra.tool.workflow")

    with patched as (m_args,):
        m_args.return_value.get.return_value = has_run_id
        assert (
            tool.api_method
            == (tool._api_method_run if has_run_id else tool._api_method_runs))

    assert (
        m_args.return_value.get.call_args
        == [("run_id",), {}])


@pytest.mark.parametrize("has_run_id", [True, False])
def test_workflow_runs_tool_endpoint_tpl(patches, has_run_id):
    """Test the WorkflowRunsTool endpoint_tpl property."""
    ctx = MagicMock()
    args = MagicMock()
    tool = workflow.WorkflowRunsTool(ctx, args)
    patched = patches(
        ("WorkflowRunsTool.args",
         dict(new_callable=PropertyMock)),
        prefix="synca.mcp.gh_extra.tool.workflow")

    with patched as (m_args,):
        m_args.return_value.get.return_value = has_run_id
        assert (
            tool.endpoint_tpl
            == (tool._endpoint_run if has_run_id else tool._endpoint_runs))

    assert (
        m_args.return_value.get.call_args
        == [("run_id",), {}])


def test_workflow_runs_tool_add_arguments(patches):
    """Test the WorkflowRunsTool add_arguments method."""
    ctx = MagicMock()
    args = MagicMock()
    tool = workflow.WorkflowRunsTool(ctx, args)
    parser = MagicMock()
    patched = patches(
        "GitHubTool.add_arguments",
        prefix="synca.mcp.gh_extra.tool.workflow")

    with patched as (m_super_add_arguments,):
        assert not tool.add_arguments(parser)

    assert (
        m_super_add_arguments.call_args
        == [(parser,), {}])
    assert (
        parser.add_argument.call_args_list[0]
        == [("owner",),
            {"required": True,
             "help": "Repository owner (username or organization)"}])
    assert (
        parser.add_argument.call_args_list[1]
        == [("repo",),
            {"required": True,
             "help": "Repository name"}])
    assert (
        parser.add_argument.call_args_list[2]
        == [("actor",),
            {"help": "Username of the user who triggered the workflow"}])
    assert (
        parser.add_argument.call_args_list[3]
        == [("branch",),
            {"help": "Branch name to filter runs"}])
    assert (
        parser.add_argument.call_args_list[4]
        == [("event",),
            {"help": "Event type (e.g. 'push', 'pull_request')"}])
    assert (
        parser.add_argument.call_args_list[5]
        == [("status",),
            {"choices": ["queued", "in_progress", "completed"],
             "help": "Status filter for workflow runs"}])
    assert (
        parser.add_argument.call_args_list[6]
        == [("per_page",),
            {"type": int,
             "help": "Number of results per page (max 100)"}])
    assert (
        parser.add_argument.call_args_list[7]
        == [("page",),
            {"type": int,
             "help": "Page number for pagination"}])
    assert (
        parser.add_argument.call_args_list[8]
        == [("created",),
            {"help": (
                "Filter by workflow run creation time "
                "(ISO 8601 format)")}])
    assert (
        parser.add_argument.call_args_list[9]
        == [("workflow_id",),
            {"help": "Workflow ID or filename to filter runs"}])
    assert (
        parser.add_argument.call_args_list[10]
        == [("exclude_pull_requests",),
            {"type": bool,
             "help": "Whether to exclude pull request workflow runs"}])
    assert (
        parser.add_argument.call_args_list[11]
        == [("check_suite_id",),
            {"type": int,
             "help": "Check suite ID to filter runs"}])
    assert (
        parser.add_argument.call_args_list[12]
        == [("head_sha",),
            {"help": "SHA to filter workflow runs"}])
    assert (
        parser.add_argument.call_args_list[13]
        == [("run_id",),
            {"type": int,
             "help": "Specific workflow run ID to retrieve"}])


def test_workflow_logs_tool_add_arguments():
    """Test the WorkflowLogsTool add_arguments method."""
    ctx = MagicMock()
    args = MagicMock()
    tool = workflow.WorkflowLogsTool(ctx, args)
    parser = MagicMock()

    assert not tool.add_arguments(parser)

    assert (
        parser.add_argument.call_args_list[0]
        == [("owner",),
            {"required": True,
             "help": "Repository owner (username or organization)"}])
    assert (
        parser.add_argument.call_args_list[1]
        == [("repo",),
            {"required": True,
             "help": "Repository name"}])
    assert (
        parser.add_argument.call_args_list[2]
        == [("run_id",),
            {"required": True,
             "type": int,
             "help": "The workflow run ID to get logs for"}])


@pytest.mark.parametrize(
    "logs_dir",
    [None, "", "/custom/workflow/logs/path"])
def test_workflow_logs_tool_write_path(patches, logs_dir):
    """Test the WorkflowLogsTool write_path cached property."""
    ctx = MagicMock()
    args = MagicMock()
    tool = workflow.WorkflowLogsTool(ctx, args)
    patched = patches(
        "os",
        "pathlib.Path",
        "print",
        "sys",
        prefix="synca.mcp.gh_extra.tool.workflow")

    with patched as (m_os, m_path, m_print, m_sys):
        m_os.environ.get.return_value = logs_dir
        assert (
            tool.write_path
            == m_path.return_value)

    assert (
        m_os.environ.get.call_args
        == [("WORKFLOW_LOGS_DIR",), {}])
    if logs_dir:
        assert (
            m_path.call_args
            == [(logs_dir,), {}])
        assert not m_print.called
        return
    assert (
        m_path.call_args
        == [("/tmp/github-workflow-logs",), {}])
    assert (
        m_print.call_args
        == [("WARNING: using default directory "
             "'/tmp/github-workflow-logs'. "
             "Set WORKFLOW_LOGS_DIR if this is not what you want",),
            {"file": m_sys.stderr}])
    assert "write_path" in tool.__dict__


def test_workflow_logs_tool_parse_output():
    """Test the WorkflowLogsTool parse_output method."""
    ctx = MagicMock()
    args = MagicMock()
    tool = workflow.WorkflowLogsTool(ctx, args)
    message = MagicMock()
    output = MagicMock()
    return_code = MagicMock()

    assert (
        tool.parse_output(message, output, return_code)
        == (return_code, output, message, {}))
