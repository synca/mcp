"""Tests for snake.mcp.server flake8 functionality."""

import asyncio
import pytest
from unittest import mock

# Import the tool we're testing
from snake.mcp.server.server import flake8


@pytest.mark.asyncio
async def test_flake8_no_issues(mock_context, temp_python_project,
                                monkeypatch):
    """Test flake8 with no issues found."""
    # Set up subprocess mock
    process_mock = mock.AsyncMock()
    process_mock.returncode = 0  # Zero indicates no issues
    process_mock.communicate.return_value = (b"", b"")

    async def mock_subprocess(*args, **kwargs):
        return process_mock
    monkeypatch.setattr(asyncio, "create_subprocess_exec", mock_subprocess)
    # Run the test
    result = await flake8(mock_context, temp_python_project.name)
    # Verify the result
    assert result["success"] is True
    assert "No issues found" in result["data"]["message"]
    assert result["data"]["has_issues"] is False
    assert result["data"]["issues_count"] == 0


@pytest.mark.asyncio
async def test_flake8_with_issues(mock_context, temp_python_project,
                                  monkeypatch):
    """Test flake8 with issues found."""
    # Set up subprocess mock with flake8 issues
    process_mock = mock.AsyncMock()
    process_mock.returncode = 1  # Non-zero indicates issues found
    process_mock.communicate.return_value = (
        b"flake8_sample.py:2:1: E401 multiple imports on one line\n"
        b"flake8_sample.py:3:31: E201 whitespace after '('\n"
        b"flake8_sample.py:4:5: E225 missing whitespace around operator\n",
        b""
    )

    async def mock_subprocess(*args, **kwargs):
        return process_mock
    monkeypatch.setattr(asyncio, "create_subprocess_exec", mock_subprocess)
    # Run the test
    result = await flake8(mock_context, temp_python_project.name)
    # Verify the result
    assert result["success"] is True
    assert "Found 3 issues" in result["data"]["message"]
    assert "E401" in result["data"]["output"]
    assert result["data"]["has_issues"] is True
    assert result["data"]["issues_count"] == 3


@pytest.mark.asyncio
async def test_flake8_max_line_length(mock_context, temp_python_project,
                                      monkeypatch):
    """Test flake8 with max_line_length parameter."""
    # Set up subprocess mock
    process_mock = mock.AsyncMock()
    process_mock.returncode = 0
    process_mock.communicate.return_value = (b"", b"")
    # Track the actual arguments
    subprocess_args = []

    async def mock_subprocess(*args, **kwargs):
        subprocess_args.extend(args)
        return process_mock
    monkeypatch.setattr(asyncio, "create_subprocess_exec", mock_subprocess)
    # Run the test with custom max line length
    max_len = 88
    result = await flake8(
        mock_context, temp_python_project.name, max_line_length=max_len
    )
    # Verify the max line length parameter was passed
    assert result["success"] is True
    expected_arg = f"--max-line-length={max_len}"
    assert expected_arg in subprocess_args


@pytest.mark.asyncio
async def test_flake8_with_custom_args(mock_context, temp_python_project,
                                       monkeypatch):
    """Test flake8 with custom arguments."""
    # Set up subprocess mock
    process_mock = mock.AsyncMock()
    process_mock.returncode = 0
    process_mock.communicate.return_value = (b"", b"")
    # Track the actual arguments
    subprocess_args = []

    async def mock_subprocess(*args, **kwargs):
        subprocess_args.extend(args)
        return process_mock
    monkeypatch.setattr(asyncio, "create_subprocess_exec", mock_subprocess)
    # Run the test with custom arguments
    custom_args = ["--ignore=E203,W503", "--exclude=.git"]
    result = await flake8(
        mock_context, temp_python_project.name, args=custom_args
    )
    # Verify custom arguments were passed
    assert result["success"] is True
    for arg in custom_args:
        assert arg in subprocess_args


@pytest.mark.asyncio
async def test_flake8_empty_output_with_issues(
        mock_context, temp_python_project, monkeypatch):
    """Test flake8 with empty output but non-zero return code."""
    # Set up subprocess mock with empty output but error code
    process_mock = mock.AsyncMock()
    process_mock.returncode = 1  # Indicates issues found
    process_mock.communicate.return_value = (b"", b"")  # But empty output

    async def mock_subprocess(*args, **kwargs):
        return process_mock
    monkeypatch.setattr(asyncio, "create_subprocess_exec", mock_subprocess)

    # Run the test
    result = await flake8(mock_context, temp_python_project.name)

    # Verify the result - should handle empty output gracefully
    assert result["success"] is True
    assert "No issues found" in result["data"]["message"]
    assert result["data"]["issues_count"] == 0
    assert result["data"]["has_issues"] is False


@pytest.mark.asyncio
async def test_flake8_error_handling(mock_context, temp_python_project,
                                     monkeypatch):
    """Test flake8 error handling."""
    # Set up subprocess mock to simulate an error
    process_mock = mock.AsyncMock()
    process_mock.returncode = 2  # Code 2 indicates an error running flake8
    process_mock.communicate.return_value = (b"", b"Error running flake8")

    async def mock_subprocess(*args, **kwargs):
        return process_mock
    monkeypatch.setattr(asyncio, "create_subprocess_exec", mock_subprocess)
    # Run the test
    result = await flake8(mock_context, temp_python_project.name)
    # Verify the error was handled
    assert result["success"] is False
    assert "flake8 failed" in result["error"]
    assert result["data"] is None
