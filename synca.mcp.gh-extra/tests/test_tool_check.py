"""Isolated tests for synca.mcp.gh_extra.tool.check."""

from unittest.mock import MagicMock

from synca.mcp.gh_extra.tool import check


def test_check_runs_tool_constructor():
    """Test the CheckRunsTool constructor."""
    ctx = MagicMock()
    args = MagicMock()
    tool = check.CheckRunsTool(ctx, args)
    assert tool.ctx == ctx
    assert tool._args == args
    assert (
        tool.endpoint_tpl
        == "/repos/{owner}/{repo}/commits/{ref}/check-runs")
    assert tool.iterable_key == "check_runs"
    assert tool._api_method == "getitems"


def test_check_runs_for_suite_tool_constructor():
    """Test the CheckRunsForSuiteTool constructor."""
    ctx = MagicMock()
    args = MagicMock()
    tool = check.CheckRunsForSuiteTool(ctx, args)
    assert tool.ctx == ctx
    assert tool._args == args
    assert (
        tool.endpoint_tpl
        == "/repos/{owner}/{repo}/check-suites/{check_suite_id}/check-runs")
    assert tool.iterable_key == "check_runs"
    assert tool._api_method == "getitems"


def test_check_suites_tool_constructor():
    """Test the CheckSuitesTool constructor."""
    ctx = MagicMock()
    args = MagicMock()
    tool = check.CheckSuitesTool(ctx, args)
    assert tool.ctx == ctx
    assert tool._args == args
    assert (
        tool.endpoint_tpl
        == "/repos/{owner}/{repo}/commits/{ref}/check-suites")
    assert tool.iterable_key == "check_suites"
    assert tool._api_method == "getitems"


def test_check_runs_tool_add_arguments(patches):
    """Test the CheckRunsTool add_arguments method."""
    ctx = MagicMock()
    args = MagicMock()
    tool = check.CheckRunsTool(ctx, args)
    parser = MagicMock()
    patched = patches(
        "GitHubTool.add_arguments",
        prefix="synca.mcp.gh_extra.tool.check")

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
        == [("ref",),
            {"required": True,
             "help": "Git reference (commit SHA, branch, or tag)"}])
    assert (
        parser.add_argument.call_args_list[3]
        == [("status",),
            {"choices": ["queued", "in_progress", "completed"],
             "help": "Status filter for check runs"}])
    assert (
        parser.add_argument.call_args_list[4]
        == [("check_name",),
            {"help": "Check name to filter check runs"}])
    assert (
        parser.add_argument.call_args_list[5]
        == [("filter",),
            {"choices": ["latest", "all"],
             "help": "Filter by 'latest' or 'all' check runs"}])
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


def test_check_runs_for_suite_tool_add_arguments(patches):
    """Test the CheckRunsForSuiteTool add_arguments method."""
    ctx = MagicMock()
    args = MagicMock()
    tool = check.CheckRunsForSuiteTool(ctx, args)
    parser = MagicMock()
    patched = patches(
        "GitHubTool.add_arguments",
        prefix="synca.mcp.gh_extra.tool.check")

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
        == [("check_suite_id",),
            {"required": True,
             "type": int,
             "help": "Check suite ID"}])
    assert (
        parser.add_argument.call_args_list[3]
        == [("status",),
            {"choices": ["queued", "in_progress", "completed"],
             "help": "Status filter for check runs"}])
    assert (
        parser.add_argument.call_args_list[4]
        == [("check_name",),
            {"help": "Check name to filter check runs"}])
    assert (
        parser.add_argument.call_args_list[5]
        == [("filter",),
            {"choices": ["latest", "all"],
             "help": "Filter by 'latest' or 'all' check runs"}])
    assert (
        parser.add_argument.call_args_list[6]
        == [("per_page",),
            {"default": 30,
             "type": int,
             "help": "Number of results per page (max 100)"}])
    assert (
        parser.add_argument.call_args_list[7]
        == [("page",),
            {"type": int,
             "help": "Page number for pagination"}])


def test_check_suites_tool_add_arguments(patches):
    """Test the CheckSuitesTool add_arguments method."""
    ctx = MagicMock()
    args = MagicMock()
    tool = check.CheckSuitesTool(ctx, args)
    parser = MagicMock()
    patched = patches(
        "GitHubTool.add_arguments",
        prefix="synca.mcp.gh_extra.tool.check")

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
        == [("ref",),
            {"required": True,
             "help": "Git reference (commit SHA, branch, or tag)"}])
    assert (
        parser.add_argument.call_args_list[3]
        == [("app_id",),
            {"type": int,
             "help": "App ID filter for check suites"}])
    assert (
        parser.add_argument.call_args_list[4]
        == [("check_name",),
            {"help": "Check name to filter check suites"}])
    assert (
        parser.add_argument.call_args_list[5]
        == [("per_page",),
            {"default": 100,
             "type": int,
             "help": "Number of results per page (max 100)"}])
    assert (
        parser.add_argument.call_args_list[6]
        == [("page",),
            {"type": int,
             "help": "Page number for pagination"}])
