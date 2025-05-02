"""Tools for working with GitHub Actions API."""

import os
import pathlib
import sys
from functools import cached_property

from synca.mcp.common.types import OutputTuple
from synca.mcp.common.util import ArgParser
from synca.mcp.gh_extra.tool.base import GitHubTool


class WorkflowRunsTool(GitHubTool):
    """Tool for listing and filtering GitHub Actions workflow runs."""
    _endpoint_run = "/repos/{owner}/{repo}/actions/runs/{run_id}"
    _endpoint_runs = "/repos/{owner}/{repo}/actions/runs"
    _api_method_run = "getitem"
    _api_method_runs = "getitems"
    iterable_key = "workflow_runs"

    @property
    def api_method(self):
        return (
            self._api_method_run
            if self.args.get("run_id")
            else self._api_method_runs)

    @property
    def endpoint_tpl(self):
        return (
            self._endpoint_run
            if self.args.get("run_id")
            else self._endpoint_runs)

    def add_arguments(self, parser: ArgParser) -> None:
        """Add workflow runs specific arguments to the parser.
        """
        super().add_arguments(parser)
        parser.add_argument(
            "owner",
            required=True,
            help="Repository owner (username or organization)")
        parser.add_argument(
            "repo",
            required=True,
            help="Repository name")
        parser.add_argument(
            "actor",
            help="Username of the user who triggered the workflow")
        parser.add_argument(
            "branch",
            help="Branch name to filter runs")
        parser.add_argument(
            "event",
            help="Event type (e.g. 'push', 'pull_request')")
        parser.add_argument(
            "status",
            choices=[
                "queued", "in_progress", "completed"],
            help="Status filter for workflow runs")
        parser.add_argument(
            "per_page",
            type=int,
            help="Number of results per page (max 100)")
        parser.add_argument(
            "page",
            type=int,
            help="Page number for pagination")
        parser.add_argument(
            "created",
            help="Filter by workflow run creation time (ISO 8601 format)")
        parser.add_argument(
            "workflow_id",
            help="Workflow ID or filename to filter runs")
        parser.add_argument(
            "exclude_pull_requests",
            type=bool,
            help="Whether to exclude pull request workflow runs")
        parser.add_argument(
            "check_suite_id",
            type=int,
            help="Check suite ID to filter runs")
        parser.add_argument(
            "head_sha",
            help="SHA to filter workflow runs")
        parser.add_argument(
            "run_id",
            type=int,
            help="Specific workflow run ID to retrieve")


class WorkflowLogsTool(GitHubTool):
    """Tool for retrieving logs from GitHub Actions workflow runs."""
    endpoint_tpl = "/repos/{owner}/{repo}/actions/runs/{run_id}/logs"
    _api_method = "download"

    @cached_property
    def write_path(self) -> pathlib.Path:
        # TODO: figure out how best to use roots
        if not (logs_dir := os.environ.get("WORKFLOW_LOGS_DIR")):
            print(
                "WARNING: using default directory "
                "'/tmp/github-workflow-logs'. "
                "Set WORKFLOW_LOGS_DIR if this is not what you want",
                file=sys.stderr)
            return pathlib.Path("/tmp/github-workflow-logs")
        return pathlib.Path(logs_dir)

    def parse_output(
            self,
            message: str,
            output: str,
            return_code: int) -> OutputTuple:
        """Process workflow logs data.

        Parses the response from the GitHub API and returns a properly
        formatted output tuple.
        """
        return (return_code, output, message, {})

    def add_arguments(self, parser: ArgParser) -> None:
        """Add workflow logs specific arguments to the parser.
        """
        parser.add_argument(
            "owner",
            required=True,
            help="Repository owner (username or organization)")
        parser.add_argument(
            "repo",
            required=True,
            help="Repository name")
        parser.add_argument(
            "run_id",
            required=True,
            type=int,
            help="The workflow run ID to get logs for")
