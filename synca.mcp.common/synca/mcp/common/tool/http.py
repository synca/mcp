from mcp.server.fastmcp import Context

from synca.mcp.common.tool.base import Tool
from synca.mcp.common.types import (
    RequestDict,
    ResponseTuple,
    ResultDict)


class HTTPTool(Tool):

    def __init__(self, ctx: Context, args: dict) -> None:
        """Initialize the tool with context and path.
        """
        self.ctx = ctx
        self._args = args

    @property
    def args(self) -> dict:
        return self._args

    @property
    def request_data(self) -> RequestDict:
        """Build the request."""
        raise NotImplementedError

    async def pipeline(self) -> ResultDict:
        """Run HTTP command handling the results."""
        return self.response(
            *self.parse_output(
                *await self.request(self.request_data)))

    async def request(
            self,
            params: RequestDict) -> ResponseTuple:
        raise NotImplementedError
