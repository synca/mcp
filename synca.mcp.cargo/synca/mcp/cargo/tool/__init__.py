"""Tools for cargo."""

from synca.mcp.cargo.tool.clippy import ClippyTool
from synca.mcp.cargo.tool.build import BuildTool
from synca.mcp.cargo.tool.check import CheckTool
from synca.mcp.cargo.tool.fmt import FmtTool
from synca.mcp.cargo.tool.test import TestTool
from synca.mcp.cargo.tool.tarpaulin import TarpaulinTool
from synca.mcp.cargo.tool.run import RunTool


__all__ = (
    "ClippyTool",
    "BuildTool",
    "CheckTool",
    "FmtTool",
    "RunTool",
    "TestTool",
    "TarpaulinTool", )
