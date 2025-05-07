"""Isolated tests for synca.mcp.common.tool."""

import pytest

from synca.mcp.common.decorator import doc


@pytest.mark.parametrize("has_docstring", [True, False])
def test_decorator_doc(has_docstring):
    """Test that the doc decorator properly sets the function docstring."""
    test_docstring = "This is a test docstring"
    if has_docstring:
        @doc(test_docstring)
        def sample_function():
            """Example docstring that should be replaced."""
            pass
    else:
        @doc(test_docstring)
        def sample_function():
            pass

    assert sample_function.__doc__ == test_docstring
