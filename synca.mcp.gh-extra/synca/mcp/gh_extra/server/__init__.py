"""GitHub Extra MCP server module."""

from synca.mcp.gh_extra.server.base import mcp
from synca.mcp.gh_extra.server.check import (
    list_check_runs_for_ref,
    list_check_runs_for_check_suite,
    list_check_suites_for_ref)
from synca.mcp.gh_extra.server.workflow import (
    get_workflow_logs,
    get_workflow_run,
    list_workflow_runs)


__all__ = (
    "get_workflow_logs",
    "get_workflow_run",
    "list_check_runs_for_ref",
    "list_check_runs_for_check_suite",
    "list_check_suites_for_ref",
    "list_workflow_runs",
    "mcp")
