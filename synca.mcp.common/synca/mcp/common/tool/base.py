
import traceback
from typing import Any

from mcp.server.fastmcp import Context

from synca.mcp.common.types import (
    OutputTuple,
    OutputInfoDict,
    ResultDict)


class Tool:
    """Base class for MCP server tools."""

    def __init__(self, ctx: Context, **kwargs: Any) -> None:
        """Initialize the tool with context and path.
        """
        self.ctx = ctx

    @property
    def tool_name(self) -> str:
        raise NotImplementedError

    async def pipeline(self) -> ResultDict:
        """Run tool on a project handling the results."""
        raise NotImplementedError

    def parse_output(
            self,
            stdout: str,
            stderr: str,
            returncode: int) -> OutputTuple:
        """Parse the tool output."""
        raise NotImplementedError

    def response(
            self,
            return_code: int,
            message: str,
            output: str,
            info: OutputInfoDict) -> ResultDict:
        """Format the final response."""
        return {
            "data": {
                "return_code": return_code,
                "message": message,
                "output": output,
                "info": info,
            }}

    async def run(self) -> ResultDict:
        """Run the tool and handle exceptions."""
        try:
            return await self.pipeline()
        except BaseException as e:
            trace = traceback.format_exc()
            tool_name = self.__class__.__name__.lower().replace("tool", "")
            error_msg = f"Failed to run {tool_name}: {str(e)}\n{trace}"
            return {
                "error": error_msg}
