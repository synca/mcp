import asyncio
import pathlib
from functools import cached_property

from mcp.server.fastmcp import Context

from synca.mcp.common.tool.base import Tool
from synca.mcp.common.types import (
    CommandTuple,
    ResponseTuple,
    ResultDict)


class CLITool(Tool):
    """Base class for MCP server tools."""

    def __init__(self, ctx: Context, path: str, args: dict) -> None:
        """Initialize the tool with context and path.
        """
        self.ctx = ctx
        self._path_str = path
        self._args = args

    @property
    def args(self) -> dict:
        return self._args

    @cached_property
    def path(self) -> pathlib.Path:
        """Get the validated path as a pathlib.Path object."""
        path = pathlib.Path(self._path_str)
        self.validate_path(path)
        return path

    @property
    def tool_path(self) -> str:
        return self.tool_name

    @property
    def command(self) -> CommandTuple:
        """Build the tool command."""
        return (self.tool_path, *self.args)

    async def execute(
            self,
            cmd: CommandTuple) -> ResponseTuple:
        """Execute the tool command."""
        process = await asyncio.create_subprocess_exec(
            *cmd,
            cwd=str(self.path),
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE)
        stdout, stderr = await process.communicate()
        return stdout.decode(), stderr.decode(), process.returncode or 0

    async def pipeline(self) -> ResultDict:
        """Run CLI command on a project handling the results."""
        return self.response(
            *self.parse_output(
                *await self.execute(self.command)))

    def validate_path(self, path: pathlib.Path) -> None:
        """Validate that the project path exists and is a directory.
        """
        if not pathlib.Path(path).exists():
            raise FileNotFoundError(f"Path '{path}' does not exist")
        if not pathlib.Path(path).is_dir():
            raise NotADirectoryError(f"Path '{path}' is not a directory")


class CLICheckTool(CLITool):
    pass
