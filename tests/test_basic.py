"""Basic tests for snake.mcp.server."""

from snake.mcp.server import server


def test_can_import_modules():
    """Test that we can import the modules."""
    # Check that the pytest tool is available
    assert hasattr(server, 'pytest')
    # Check that the flake8 tool is available
    assert hasattr(server, 'flake8')
