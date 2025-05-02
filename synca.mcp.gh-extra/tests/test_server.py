"""Isolated tests for synca.mcp.gh_extra.server."""

import inspect

from mcp.server.fastmcp import FastMCP

from synca.mcp.gh_extra import server


def test_fastmcp_initialization():
    """Test the FastMCP initialization in server.py."""
    assert isinstance(server.mcp, FastMCP)
    assert server.mcp.name == "GitHub extra"
    assert (
        set(["list_workflow_runs", "get_workflow_run", "get_workflow_logs",
             "list_check_runs_for_ref", "list_check_runs_for_check_suite",
             "list_check_suites_for_ref"])
        <= set(f[0] for f in inspect.getmembers(server, inspect.isfunction)))
