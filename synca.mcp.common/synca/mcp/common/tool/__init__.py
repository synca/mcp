"""Base Tool class for MCP server tools."""

from synca.mcp.common.tool.base import Tool
from synca.mcp.common.tool.cli import CLICheckTool, CLITool
from synca.mcp.common.tool.http import HTTPTool


__all__ = (
    "CLICheckTool",
    "CLITool",
    "HTTPTool",
    "Tool")
