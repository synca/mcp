"""Tests for snake.mcp.server common functionality."""

import pytest

# Import after path modification
from snake.mcp.server.server import (
    pytest as pytest_tool,
    flake8,
    mypy,
)


@pytest.mark.asyncio
async def test_path_validation(mock_context):
    """Test path validation for Python tools."""
    invalid_path = "/non/existent/path"
    # Test each tool with an invalid path
    tools = [
        pytest_tool,
        flake8,
        mypy,
    ]
    for tool in tools:
        result = await tool(mock_context, invalid_path)
        assert result["success"] is False
        assert "does not exist" in result["error"]
        assert result["data"] is None
