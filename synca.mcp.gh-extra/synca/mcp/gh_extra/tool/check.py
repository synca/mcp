"""Tools for working with GitHub Checks API."""

from synca.mcp.common.util import ArgParser
from synca.mcp.gh_extra.tool.base import GitHubTool


class CheckRunsTool(GitHubTool):
    """Tool for retrieving check runs for a Git reference."""
    endpoint_tpl = "/repos/{owner}/{repo}/commits/{ref}/check-runs"
    iterable_key = "check_runs"
    _api_method = "getitems"

    def add_arguments(self, parser: ArgParser) -> None:
        """Add check runs specific arguments to the parser."""
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
            "ref",
            required=True,
            help="Git reference (commit SHA, branch, or tag)")
        parser.add_argument(
            "status",
            choices=["queued", "in_progress", "completed"],
            help="Status filter for check runs")
        parser.add_argument(
            "check_name",
            help="Check name to filter check runs")
        parser.add_argument(
            "filter",
            choices=["latest", "all"],
            help="Filter by 'latest' or 'all' check runs")
        parser.add_argument(
            "per_page",
            type=int,
            help="Number of results per page (max 100)")
        parser.add_argument(
            "page",
            type=int,
            help="Page number for pagination")


class CheckRunsForSuiteTool(GitHubTool):
    """Tool for retrieving check runs for a specific check suite."""
    endpoint_tpl = (
        "/repos/{owner}/{repo}/check-suites/{check_suite_id}/check-runs")
    iterable_key = "check_runs"
    _api_method = "getitems"

    def add_arguments(self, parser: ArgParser) -> None:
        """Add check runs for suite specific arguments to the parser."""
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
            "check_suite_id",
            required=True,
            type=int,
            help="Check suite ID")
        parser.add_argument(
            "status",
            choices=["queued", "in_progress", "completed"],
            help="Status filter for check runs")
        parser.add_argument(
            "check_name",
            help="Check name to filter check runs")
        parser.add_argument(
            "filter",
            choices=["latest", "all"],
            help="Filter by 'latest' or 'all' check runs")
        parser.add_argument(
            "per_page",
            default=30,
            type=int,
            help="Number of results per page (max 100)")
        parser.add_argument(
            "page",
            type=int,
            help="Page number for pagination")


class CheckSuitesTool(GitHubTool):
    """Tool for retrieving check suites for a specific Git reference."""
    endpoint_tpl = "/repos/{owner}/{repo}/commits/{ref}/check-suites"
    iterable_key = "check_suites"
    _api_method = "getitems"

    def add_arguments(self, parser: ArgParser) -> None:
        """Add check suites specific arguments to the parser."""
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
            "ref",
            required=True,
            help="Git reference (commit SHA, branch, or tag)")
        parser.add_argument(
            "app_id",
            type=int,
            help="App ID filter for check suites")
        parser.add_argument(
            "check_name",
            help="Check name to filter check suites")
        parser.add_argument(
            "per_page",
            default=100,
            type=int,
            help="Number of results per page (max 100)")
        parser.add_argument(
            "page",
            type=int,
            help="Page number for pagination")
