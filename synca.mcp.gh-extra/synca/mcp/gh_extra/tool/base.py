"""Base Tool class for GitHub Extra MCP server tools."""

import os
import pathlib
from functools import cached_property
from typing import Any

import aiohttp
from gidgethub import GitHubException
from mcp.server.fastmcp import Context

from synca.mcp.common.tool import HTTPTool
from synca.mcp.common.types import APIRequestDict, OutputTuple, ResponseTuple
from synca.mcp.common.util import ArgParser, JQFilter
from synca.mcp.gh_extra import errors, util


class GitHubTool(HTTPTool[APIRequestDict]):
    """Base class for GitHub Extra tools."""
    _api_method: str | None = None
    endpoint_tpl = ""
    iterable_key: str | None = None

    def __init__(self, ctx: Context, args: dict) -> None:
        """Initialize with context and arguments."""
        self.ctx = ctx
        self._args = args

    @property
    def api_method(self) -> str:
        if not self._api_method:
            raise errors.GitHubToolError(
                f"_api_method must be set for: {self.__class__.__name__}")
        return self._api_method

    @property
    def arg_parser(self) -> ArgParser:
        """Create an argument parser for this tool."""
        parser = ArgParser()
        self.add_arguments(parser)
        return parser

    @cached_property
    def args(self) -> dict[str, Any]:
        """Parse and validate arguments."""
        return self.arg_parser.parse_dict(self._args)

    @property
    def endpoint(self) -> str:
        """GitHub API endpoint to call."""
        return self.endpoint_tpl.format(**self.args)

    @cached_property
    def gh_api(self) -> util.GitHubAPI:
        """Parse and validate arguments."""
        return util.GitHubAPI(
            self.gh_token,
            write_path=self.write_path)

    @property
    def gh_token(self) -> str:
        """Get the GitHub API token from environment."""
        if token := os.environ.get("GITHUB_TOKEN"):
            return token
        raise ValueError(
            "GITHUB_TOKEN environment variable is required "
            "for GitHub API access")

    @property
    def request_data(self) -> APIRequestDict:
        """Build the GitHub API request information for workflow runs.
        """
        return dict(
            method=self.api_method,
            iterable_key=self.iterable_key,
            pages=self.args.get("pages", 1),
            endpoint=self.endpoint,
            params=self.args)

    @property
    def write_path(self) -> pathlib.Path | None:
        return None

    def parse_output(
            self,
            stdout: str,
            stderr: str,
            returncode: int) -> OutputTuple:
        """Parse and filter the GitHub API response for workflow runs.
        """
        return (
            returncode,
            stderr,
            JQFilter.apply(stdout, self.args.get("jq")),
            {})

    async def request(
            self,
            request: APIRequestDict) -> ResponseTuple:
        """Execute a GitHub API request."""
        try:
            async with self.gh_api as api:
                return await self._handle_request(api, request)
        except GitHubException as e:
            raise errors.GitHubRequestError(
                f"GitHub API error: {str(e)}",
                status_code=getattr(e, "status_code", 500),
                response_data=getattr(e, "data", None))
        except aiohttp.ClientError as e:
            raise errors.GitHubRequestError(
                f"HTTP client error: {str(e)}", status_code=None)

    async def _handle_request(
            self,
            api: util.GitHubAPI,
            request: APIRequestDict) -> ResponseTuple:
        match request["method"]:
            case "download":
                return await api.download(
                    request["endpoint"],
                    request["params"])
            case "getitem":
                return await api.getitem(
                    request["endpoint"],
                    request["params"])
            case "getitems":
                return await api.getitems(
                    request["endpoint"],
                    request["params"],
                    iterable_key=request.get("iterable_key"))
        raise errors.GitHubRequestError(
            f"Unsupported HTTP method: {request['method']}",
            status_code=400)

    def add_arguments(self, parser: ArgParser) -> None:
        """Add tool-specific arguments to the parser."""
        parser.add_argument(
            "jq",
            required=False,
            help="jq filter to apply to the output")
