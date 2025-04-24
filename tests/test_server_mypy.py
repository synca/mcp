"""Tests for snake.mcp.server mypy functionality."""

import asyncio
import os
import pytest
from unittest import mock

# Import the tool we're testing
from snake.mcp.server.server import mypy


@pytest.mark.asyncio
async def test_mypy_no_issues(mock_context, temp_python_project,
                              monkeypatch):
    """Test mypy with no issues found."""
    # Set up subprocess mock
    process_mock = mock.AsyncMock()
    process_mock.returncode = 0  # Zero indicates no issues
    process_mock.communicate.return_value = (b"", b"")

    async def mock_subprocess(*args, **kwargs):
        return process_mock
    monkeypatch.setattr(asyncio, "create_subprocess_exec", mock_subprocess)
    # Run the test
    result = await mypy(mock_context, temp_python_project.name)
    # Verify the result
    assert result["success"] is True
    assert "No issues found" in result["data"]["message"]
    assert result["data"]["has_issues"] is False
    assert result["data"]["issues_count"] == 0


@pytest.mark.asyncio
async def test_mypy_with_issues(mock_context, temp_python_project,
                                monkeypatch):
    """Test mypy with issues found."""
    # Set up subprocess mock with mypy issues
    process_mock = mock.AsyncMock()
    process_mock.returncode = 1  # Non-zero indicates issues found
    process_mock.communicate.return_value = (
        b"mypy_sample.py:3: error: Function is missing a type annotation\n"
        b"mypy_sample.py:6: error: Incompatible return value type\n"
        b"mypy_sample.py:11: error: Incompatible return value type\n",
        b""
    )

    async def mock_subprocess(*args, **kwargs):
        return process_mock
    monkeypatch.setattr(asyncio, "create_subprocess_exec", mock_subprocess)
    # Run the test
    result = await mypy(mock_context, temp_python_project.name)
    # Verify the result
    assert result["success"] is True
    assert "Found 3 type issues" in result["data"]["message"]
    assert "error: Function is missing a type annotation" in (
        result["data"]["output"]
    )
    assert result["data"]["has_issues"] is True
    assert result["data"]["issues_count"] == 3


@pytest.mark.asyncio
async def test_mypy_disallow_untyped_defs(mock_context, temp_python_project,
                                          monkeypatch):
    """Test mypy with disallow_untyped_defs parameter."""
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
    # Run the test with disallow_untyped_defs=True
    result = await mypy(
        mock_context, temp_python_project.name, disallow_untyped_defs=True
    )
    # Verify the parameter was passed
    assert result["success"] is True
    assert "--disallow-untyped-defs" in subprocess_args


@pytest.mark.asyncio
async def test_mypy_disallow_incomplete_defs(mock_context, temp_python_project,
                                             monkeypatch):
    """Test mypy with disallow_incomplete_defs parameter."""
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
    # Run the test with disallow_incomplete_defs=True
    result = await mypy(
        mock_context, temp_python_project.name, disallow_incomplete_defs=True
    )
    # Verify the parameter was passed
    assert result["success"] is True
    assert "--disallow-incomplete-defs" in subprocess_args


@pytest.mark.asyncio
async def test_mypy_with_custom_args(mock_context, temp_python_project,
                                     monkeypatch):
    """Test mypy with custom arguments."""
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
    custom_args = ["--ignore-missing-imports", "--no-implicit-optional"]
    result = await mypy(
        mock_context, temp_python_project.name, args=custom_args
    )
    # Verify custom arguments were passed
    assert result["success"] is True
    for arg in custom_args:
        assert arg in subprocess_args


@pytest.mark.asyncio
async def test_mypy_find_config_file(mock_context, temp_python_project,
                                     monkeypatch):
    """Test mypy finding a configuration file."""
    # Create a mypy.ini file in the project
    with open(f"{temp_python_project.name}/mypy.ini", "w") as f:
        f.write("[mypy]\nexclude = tests/\n")

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

    # Run the test
    result = await mypy(mock_context, temp_python_project.name)

    # Verify it found and used the config file
    assert result["success"] is True
    assert "--config-file" in subprocess_args
    assert f"{temp_python_project.name}/mypy.ini" in subprocess_args


@pytest.mark.asyncio
async def test_mypy_parent_directory_config(mock_context, temp_python_project,
                                            monkeypatch):
    """Test mypy finding configuration in parent directory."""
    # Create a subdirectory and a config file in the parent directory
    os.makedirs(f"{temp_python_project.name}/subdir", exist_ok=True)
    with open(f"{temp_python_project.name}/mypy.ini", "w") as f:
        f.write("[mypy]\nexclude = tests/\n")

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

    # Run the test on the subdirectory
    result = await mypy(mock_context, f"{temp_python_project.name}/subdir")

    # Verify it found and used the parent's config file
    assert result["success"] is True
    assert "--config-file" in subprocess_args
    assert f"{temp_python_project.name}/mypy.ini" in subprocess_args


@pytest.mark.asyncio
async def test_mypy_parent_config_not_exist(mock_context, temp_python_project,
                                            monkeypatch):
    """Test mypy when parent config doesn't exist."""
    # Create a nested directory structure with no mypy.ini files
    subdir = os.path.join(temp_python_project.name, "subdir")
    os.makedirs(subdir, exist_ok=True)

    # Create a simple Python file for testing
    with open(os.path.join(subdir, "test.py"), "w") as f:
        f.write("x: int = 'string'  # Type error\n")

    # Set up subprocess mock
    process_mock = mock.AsyncMock()
    process_mock.returncode = 1  # Type issues found
    process_mock.communicate.return_value = (
        b"subdir/test.py:1: error: Incompatible types\n",
        b""
    )

    # Mock the subprocess to return our custom output
    async def mock_subprocess(*args, **kwargs):
        return process_mock
    monkeypatch.setattr(asyncio, "create_subprocess_exec", mock_subprocess)

    # Run the test with our setup
    result = await mypy(mock_context, subdir)

    # Verify result
    assert result["success"] is True
    assert "Found 1 type issues" in result["data"]["message"]
    assert result["data"]["issues_count"] == 1


@pytest.mark.asyncio
async def test_mypy_exclude_option(mock_context, temp_python_project,
                                   monkeypatch):
    """Test mypy with exclude option."""
    # Create tests directory
    os.makedirs(f"{temp_python_project.name}/tests", exist_ok=True)

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

    # Run the test with exclude
    exclude_paths = ["tests/", "examples/"]
    result = await mypy(
        mock_context, temp_python_project.name,
        exclude=exclude_paths
    )

    # Verify both exclude paths were passed
    assert result["success"] is True
    for path in exclude_paths:
        assert f"--exclude={path}" in subprocess_args


@pytest.mark.asyncio
async def test_mypy_auto_exclude_tests(mock_context, temp_python_project,
                                       monkeypatch):
    """Test mypy auto-excluding tests directory."""
    # Create tests directory
    os.makedirs(f"{temp_python_project.name}/tests", exist_ok=True)

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

    # Run the test without explicit exclude
    result = await mypy(mock_context, temp_python_project.name)

    # Verify tests directory was automatically excluded
    assert result["success"] is True
    assert "--exclude=tests/" in subprocess_args


@pytest.mark.asyncio
async def test_mypy_auto_exclude_permission_error(
        mock_context, temp_python_project, monkeypatch):
    """Test mypy with permission error during auto-exclude."""
    # Mock isdir to raise PermissionError when checking tests directory
    def mock_isdir(path):
        if "tests" in str(path):
            raise PermissionError("Permission denied")
        return True

    # Apply the mock
    monkeypatch.setattr(os.path, "isdir", mock_isdir)

    # Set up subprocess mock
    process_mock = mock.AsyncMock()
    process_mock.returncode = 0
    process_mock.communicate.return_value = (b"", b"")

    # Mock the subprocess to return our custom output
    async def mock_subprocess(*args, **kwargs):
        return process_mock
    monkeypatch.setattr(asyncio, "create_subprocess_exec", mock_subprocess)

    # Run the test
    result = await mypy(mock_context, temp_python_project.name)

    # Verify result (should succeed despite permission error)
    assert result["success"] is True
    assert "No issues found" in result["data"]["message"]


@pytest.mark.asyncio
async def test_mypy_error_handling(mock_context, temp_python_project,
                                   monkeypatch):
    """Test mypy error handling."""
    # Set up subprocess mock to simulate an error
    process_mock = mock.AsyncMock()
    # Code higher than 1 indicates an error running mypy
    process_mock.returncode = 2
    process_mock.communicate.return_value = (b"", b"Error running mypy")

    async def mock_subprocess(*args, **kwargs):
        return process_mock
    monkeypatch.setattr(asyncio, "create_subprocess_exec", mock_subprocess)
    # Run the test
    result = await mypy(mock_context, temp_python_project.name)
    # Verify the error was handled
    assert result["success"] is False
    assert "mypy failed" in result["error"]
    assert result["data"] is None


@pytest.mark.asyncio
async def test_mypy_empty_stderr_with_error(
        mock_context, temp_python_project, monkeypatch):
    """Test mypy with error code but empty stderr."""
    # Set up subprocess mock to simulate an error with empty stderr
    process_mock = mock.AsyncMock()
    process_mock.returncode = 2  # Error code
    process_mock.communicate.return_value = (b"", b"")  # Empty stderr

    async def mock_subprocess(*args, **kwargs):
        return process_mock
    monkeypatch.setattr(asyncio, "create_subprocess_exec", mock_subprocess)

    # Run the test
    result = await mypy(mock_context, temp_python_project.name)

    # Verify error handling with empty stderr
    assert result["success"] is False
    assert "mypy failed" in result["error"]
    assert result["data"] is None
