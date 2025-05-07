from typing import Generic, TypeVar

from mcp.server.fastmcp import Context

from synca.mcp.common.tool.base import Tool
from synca.mcp.common.types import (
    RequestDict,
    ResponseTuple,
    ResultDict)

T = TypeVar("T", bound=RequestDict)


class HTTPTool(Tool, Generic[T]):

    def __init__(self, ctx: Context, args: dict) -> None:
        """Initialize the tool with context and path.
        """
        self.ctx = ctx
        self._args = args

    @property
    def args(self) -> dict:
        raise NotImplementedError

    @property
    def request_data(self) -> T:
        """Build the request."""
        raise NotImplementedError

    async def pipeline(self) -> ResultDict:
        """Run HTTP command handling the results."""
        return self.response(
            *self.parse_output(
                *await self.request(self.request_data)))

    async def request(
            self,
            params: T) -> ResponseTuple:
        raise NotImplementedError
