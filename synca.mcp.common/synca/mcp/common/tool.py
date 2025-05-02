"""Base Tool class for MCP server tools."""

import asyncio
import pathlib
import traceback
from functools import cached_property
from typing import Any

from mcp.server.fastmcp import Context

from synca.mcp.common.types import ResultDict, OutputTuple, OutputInfoDict


class Tool:
    """Base class for MCP server tools."""

    def __init__(self, ctx: Context, **kwargs: Any) -> None:
        """Initialize the tool with context and path.
        """
        self.ctx = ctx

    @property
    def config_args(self) -> tuple[str, ...]:
        return ()

    @property
    def tool_name(self) -> str:
        raise NotImplementedError

    def command(
            self,
            args: list[str] | None = None) -> list[str]:
        """Build the tool command."""
        raise NotImplementedError

    async def execute(
            self,
            cmd: list[str]) -> tuple[str, str, int]:
        """Execute the tool command."""
        raise NotImplementedError

    async def handle(
            self,
            args: list[str] | None = None) -> ResultDict:
        """Run tool on a Python project."""
        return self.response(
            *self.parse_output(
                *await self.execute(
                    self.command(args))))

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

    async def run(self, *args: Any, **kwargs: Any) -> ResultDict:
        """Run the tool and handle exceptions."""
        try:
            return await self.handle(*args, **kwargs)
        except BaseException as e:
            trace = traceback.format_exc()
            tool_name = self.__class__.__name__.lower().replace("tool", "")
            error_msg = f"Failed to run {tool_name}: {str(e)}\n{trace}"
            return {
                "error": error_msg}


class CLITool(Tool):
    """Base class for MCP server tools."""

    def __init__(self, ctx: Context, path: str) -> None:
        """Initialize the tool with context and path.
        """
        self.ctx = ctx
        self._path_str = path

    @cached_property
    def path(self) -> pathlib.Path:
        """Get the validated path as a pathlib.Path object."""
        path = pathlib.Path(self._path_str)
        self.validate_path(path)
        return path

    @property
    def tool_path(self) -> str:
        return self.tool_name

    def command(
            self,
            args: list[str] | None = None) -> list[str]:
        """Build the tool command."""
        return [self.tool_path, *self.config_args, *(args or [])]

    async def execute(
            self,
            cmd: list[str]) -> tuple[str, str, int]:
        """Execute the tool command."""
        process = await asyncio.create_subprocess_exec(
            *cmd,
            cwd=str(self.path),
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE)
        stdout, stderr = await process.communicate()
        return stdout.decode(), stderr.decode(), process.returncode or 0

    def validate_path(self, path: pathlib.Path) -> None:
        """Validate that the project path exists and is a directory.
        """
        if not pathlib.Path(path).exists():
            raise FileNotFoundError(f"Path '{path}' does not exist")
        if not pathlib.Path(path).is_dir():
            raise NotADirectoryError(f"Path '{path}' is not a directory")


class CheckTool(CLITool):
    pass
