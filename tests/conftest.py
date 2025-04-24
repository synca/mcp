"""Test configuration for pytest."""

import pathlib
import tempfile
import pytest


class MockContext:
    """Mock Context for testing."""
    pass


@pytest.fixture
def mock_context():
    """Fixture to provide a mock context."""
    return MockContext()


@pytest.fixture
def temp_python_project():
    """Fixture to create a temporary Python project for testing."""
    temp_dir = tempfile.TemporaryDirectory()
    project_path = pathlib.Path(temp_dir.name)
    # Create a simple Python file for testing
    with open(project_path / "test_sample.py", "w") as f:
        f.write("""
def test_passing():
    assert True

def test_failing():
    assert False
""")
    # Create a file with some PEP8 issues for flake8 testing
    with open(project_path / "flake8_sample.py", "w") as f:
        f.write("""
import os, sys
def function_with_too_many_spaces(  arg1,   arg2 ):
    x=1+2 # Missing spaces around operator
    return None""")
    # Create a file with type issues for mypy testing
    with open(project_path / "mypy_sample.py", "w") as f:
        f.write("""
from typing import List, Dict, Optional

def add_numbers(a, b):  # Missing type annotations
    return a + b

def greet(name: str) -> int:  # Incorrect return type
    return f"Hello, {name}"

def process_data(data: List[int]) -> None:
    result = 0
    for item in data:
        result += item
    return result  # Should return None, not an int
""")
    yield temp_dir
    # Cleanup happens automatically when the fixture goes out of scope
    temp_dir.cleanup()
