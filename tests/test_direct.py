"""Direct tests for snake-mcp-server."""


def test_server_file_exists():
    """Test that the server.py file exists and has the expected content."""
    import os
    # Get the path to the server.py file
    server_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        'snake', 'mcp', 'server', 'server.py'
    )
    # Check that the file exists
    assert os.path.exists(server_path)
    # Read the file content
    with open(server_path, 'r') as f:
        content = f.read()
    # Check that the file contains the expected content
    assert '@mcp.tool()' in content
    assert 'async def pytest(' in content
    assert 'async def flake8(' in content
