"""Tests for snake.mcp.server pytest functionality."""

import asyncio
import pytest
from unittest import mock

# Import the tool we're testing
from snake.mcp.server.server import pytest as pytest_tool


@pytest.mark.asyncio
async def test_pytest_success(mock_context, temp_python_project,
                              monkeypatch):
    """Test pytest with successful execution."""
    # Set up subprocess mock
    process_mock = mock.AsyncMock()
    process_mock.returncode = 0
    process_mock.communicate.return_value = (
        b"===== test session starts =====\n"
        b"collected 2 items\n\n"
        b"test_sample.py ..\n\n"
        b"===== 2 passed in 0.01s =====\n",
        b""
    )

    async def mock_subprocess(*args, **kwargs):
        return process_mock
    monkeypatch.setattr(asyncio, "create_subprocess_exec", mock_subprocess)
    # Run the test
    result = await pytest_tool(mock_context, temp_python_project.name)
    # Verify the result
    assert result["success"] is True
    assert "All tests passed successfully" in result["data"]["message"]
    assert "2 passed" in result["data"]["output"]
    assert result["data"]["project_path"] == temp_python_project.name
    assert result["data"]["test_summary"]["passed"] == 2
    assert result["data"]["test_summary"]["total"] == 2


@pytest.mark.asyncio
async def test_pytest_with_verbose(mock_context, temp_python_project,
                                   monkeypatch):
    """Test pytest with verbose flag."""
    # Set up subprocess mock
    process_mock = mock.AsyncMock()
    process_mock.returncode = 0
    process_mock.communicate.return_value = (b"Verbose output", b"")
    # Track the actual arguments
    subprocess_args = []

    async def mock_subprocess(*args, **kwargs):
        subprocess_args.extend(args)
        return process_mock
    monkeypatch.setattr(asyncio, "create_subprocess_exec", mock_subprocess)
    # Run the test with verbose flag
    result = await pytest_tool(mock_context, temp_python_project.name,
                               verbose=True)
    # Verify the verbose flag was passed
    assert result["success"] is True
    assert "-v" in subprocess_args


@pytest.mark.asyncio
async def test_pytest_with_custom_args(mock_context, temp_python_project,
                                       monkeypatch):
    """Test pytest with custom arguments."""
    # Set up subprocess mock
    process_mock = mock.AsyncMock()
    process_mock.returncode = 0
    process_mock.communicate.return_value = (b"Custom args output", b"")
    # Track the actual arguments
    subprocess_args = []

    async def mock_subprocess(*args, **kwargs):
        subprocess_args.extend(args)
        return process_mock
    monkeypatch.setattr(asyncio, "create_subprocess_exec", mock_subprocess)
    # Run the test with custom arguments
    custom_args = ["--cov=mypackage", "-xvs"]
    test_path = temp_python_project.name
    result = await pytest_tool(mock_context, test_path, args=custom_args)
    # Verify custom arguments were passed
    assert result["success"] is True
    for arg in custom_args:
        assert arg in subprocess_args


@pytest.mark.asyncio
async def test_pytest_failure(mock_context, temp_python_project,
                              monkeypatch):
    """Test pytest with failing tests."""
    # Set up subprocess mock
    process_mock = mock.AsyncMock()
    process_mock.returncode = 1  # Non-zero indicates test failures
    process_mock.communicate.return_value = (
        b"===== test session starts =====\n"
        b"collected 2 items\n\n"
        b"test_sample.py .F\n\n"
        b"===== 1 passed, 1 failed in 0.01s =====\n",
        b""
    )

    async def mock_subprocess(*args, **kwargs):
        return process_mock
    monkeypatch.setattr(asyncio, "create_subprocess_exec", mock_subprocess)
    # Run the test
    result = await pytest_tool(mock_context, temp_python_project.name)
    # Verify the result - should still be success since tool ran correctly
    assert result["success"] is True
    assert "Some tests failed" in result["data"]["message"]
    assert "1 passed, 1 failed" in result["data"]["output"]
    assert result["data"]["test_summary"]["passed"] == 1
    assert result["data"]["test_summary"]["failed"] == 1
    assert result["data"]["test_summary"]["total"] == 2


@pytest.mark.asyncio
async def test_pytest_test_summary_parsing(mock_context, temp_python_project,
                                           monkeypatch):
    """Test pytest result parsing with complex summary."""
    # Set up subprocess mock with output containing skipped and xfailed tests
    process_mock = mock.AsyncMock()
    process_mock.returncode = 0
    process_mock.communicate.return_value = (
        b"===== test session starts =====\n"
        b"collected 5 items\n\n"
        b"test_sample.py ..sxX\n\n"
        b"===== 2 passed, 1 skipped, 1 xfailed, 1 xpassed in 0.01s =====\n",
        b""
    )

    async def mock_subprocess(*args, **kwargs):
        return process_mock
    monkeypatch.setattr(asyncio, "create_subprocess_exec", mock_subprocess)
    # Run the test
    result = await pytest_tool(mock_context, temp_python_project.name)
    # Verify complex test summary parsing
    assert result["success"] is True
    assert result["data"]["test_summary"]["passed"] == 2
    assert result["data"]["test_summary"]["skipped"] == 1
    assert result["data"]["test_summary"]["xfailed"] == 1
    assert result["data"]["test_summary"]["xpassed"] == 1
    test_total = result["data"]["test_summary"]["total"]
    assert test_total == 5


@pytest.mark.asyncio
async def test_pytest_with_coverage(mock_context, temp_python_project,
                                    monkeypatch):
    """Test pytest with coverage option."""
    # Set up subprocess mock with coverage output
    process_mock = mock.AsyncMock()
    process_mock.returncode = 0
    process_mock.communicate.return_value = (
        b"===== test session starts =====\n"
        b"collected 2 items\n\n"
        b"test_sample.py ..\n\n"
        b"============================== 2 passed in 0.01s =====\n"
        b"=============================== coverage =================\n"
        b"Name                           Stmts   Miss  Cover\n"
        b"--------------------------------------------------\n"
        b"test_sample.py                     5      0   100%\n"
        b"TOTAL                              5      0   100%\n",
        b""
    )

    async def mock_subprocess(*args, **kwargs):
        return process_mock
    monkeypatch.setattr(asyncio, "create_subprocess_exec", mock_subprocess)
    # Run the test with coverage
    result = await pytest_tool(
        mock_context, temp_python_project.name, coverage=True
    )
    # Verify the result
    assert result["success"] is True
    assert "All tests passed successfully" in result["data"]["message"]
    assert result["data"]["coverage"] is not None
    assert result["data"]["coverage"]["total"] == 100.0
    assert "test_sample.py" in result["data"]["coverage"]["by_file"]
    assert result["data"]["coverage"]["by_file"]["test_sample.py"] == 100.0


@pytest.mark.asyncio
async def test_pytest_with_coverage_source(mock_context, temp_python_project,
                                           monkeypatch):
    """Test pytest with coverage_source option."""
    # Set up subprocess mock
    process_mock = mock.AsyncMock()
    process_mock.returncode = 0
    process_mock.communicate.return_value = (
        b"===== test session starts =====\n"
        b"collected 2 items\n\n"
        b"test_sample.py ..\n\n"
        b"============================== 2 passed in 0.01s =====\n"
        b"=============================== coverage =================\n"
        b"Name                           Stmts   Miss  Cover\n"
        b"--------------------------------------------------\n"
        b"mypackage/__init__.py              0      0   100%\n"
        b"TOTAL                              0      0   100%\n",
        b""
    )

    # Track the actual arguments
    subprocess_args = []

    async def mock_subprocess(*args, **kwargs):
        subprocess_args.extend(args)
        return process_mock
    monkeypatch.setattr(asyncio, "create_subprocess_exec", mock_subprocess)

    # Run the test with coverage_source
    result = await pytest_tool(
        mock_context, temp_python_project.name,
        coverage=True, coverage_source="mypackage"
    )

    # Verify the parameter was passed
    assert result["success"] is True
    assert "--cov=mypackage" in subprocess_args
    assert result["data"]["coverage"] is not None
    assert result["data"]["coverage"]["total"] == 100.0


@pytest.mark.asyncio
async def test_pytest_coverage_parsing_error(mock_context, temp_python_project,
                                             monkeypatch):
    """Test pytest with coverage parsing error."""
    # Set up subprocess mock with malformed coverage output
    process_mock = mock.AsyncMock()
    process_mock.returncode = 0
    process_mock.communicate.return_value = (
        b"===== test session starts =====\n"
        b"collected 2 items\n\n"
        b"test_sample.py ..\n\n"
        b"============================== 2 passed in 0.01s =====\n"
        b"=============================== coverage =================\n"
        b"Name                           Stmts   Miss  Cover\n"
        b"--------------------------------------------------\n"
        b"This line has no valid coverage data\n"
        b"TOTAL                              INVALID   DATA\n",
        b""
    )

    async def mock_subprocess(*args, **kwargs):
        return process_mock
    monkeypatch.setattr(asyncio, "create_subprocess_exec", mock_subprocess)

    # Run the test with coverage
    result = await pytest_tool(
        mock_context, temp_python_project.name, coverage=True
    )

    # Verify it handles parsing errors gracefully
    assert result["success"] is True
    assert result["data"]["coverage"] is not None
    # Total should be 0.0 when parsing fails
    assert result["data"]["coverage"]["total"] == 0.0
    assert result["data"]["coverage"]["by_file"] == {}


@pytest.mark.asyncio
async def test_pytest_subprocess_exception(mock_context, temp_python_project,
                                           monkeypatch):
    """Test pytest with subprocess exception."""
    # Make the subprocess call raise an exception
    async def mock_subprocess_error(*args, **kwargs):
        raise RuntimeError("Command failed")
    monkeypatch.setattr(
        asyncio, "create_subprocess_exec", mock_subprocess_error
    )

    # Run the test
    result = await pytest_tool(mock_context, temp_python_project.name)

    # Verify the error was handled
    assert result["success"] is False
    assert "Failed to run pytest" in result["error"]
    assert "Command failed" in result["error"]
    assert result["data"] is None


@pytest.mark.asyncio
async def test_pytest_summary_parsing_exception(
        mock_context, temp_python_project, monkeypatch):
    """Test pytest when summary parsing raises an exception."""
    # Create a mock with output that will cause parsing to fail
    process_mock = mock.AsyncMock()
    process_mock.returncode = 0
    # Invalid format for summary line
    process_mock.communicate.return_value = (
        b"===== test session starts =====\n"
        b"Corrupted output that won't parse correctly\n",
        b""
    )

    async def mock_subprocess(*args, **kwargs):
        return process_mock
    monkeypatch.setattr(asyncio, "create_subprocess_exec", mock_subprocess)

    # Run the test
    result = await pytest_tool(mock_context, temp_python_project.name)

    # Should succeed with default values for summary fields
    assert result["success"] is True
    assert result["data"]["test_summary"]["total"] == 0
    assert result["data"]["test_summary"]["passed"] == 0


@pytest.mark.asyncio
async def test_pytest_nonstandard_exit_code(
        mock_context, temp_python_project, monkeypatch):
    """Test pytest with a non-standard exit code (not 0 or 1)."""
    process_mock = mock.AsyncMock()
    # Exit code 5 (no tests collected)
    process_mock.returncode = 5
    process_mock.communicate.return_value = (
        b"===== test session starts =====\n"
        b"collected 0 items\n\n"
        b"====== no tests ran in 0.01s ======\n",
        b""
    )

    async def mock_subprocess(*args, **kwargs):
        return process_mock
    monkeypatch.setattr(asyncio, "create_subprocess_exec", mock_subprocess)

    # Run the test
    result = await pytest_tool(mock_context, temp_python_project.name)

    # Should still succeed and handle as test failure
    assert result["success"] is True
    assert "Some tests failed" in result["data"]["message"]
    assert "no tests ran" in result["data"]["output"]
