"""Isolated tests for synca.mcp.common.util.jq."""

from unittest.mock import MagicMock

import pytest

from synca.mcp.common.util import JQFilter


@pytest.mark.parametrize("jq_filter", [None, MagicMock()])
def test_jq_filter_apply(patches, jq_filter):
    """Test the JQFilter.apply method.

    Verifies that JQFilter.apply correctly handles jq filters.
    """
    json_str = MagicMock()
    patched = patches(
        "jq",
        "str",
        prefix="synca.mcp.common.util.jq")

    with patched as (m_jq, m_str):
        if jq_filter is None:
            assert (
                JQFilter.apply(json_str, jq_filter)
                == json_str)
        else:
            assert (
                JQFilter.apply(json_str, jq_filter)
                == m_str.return_value)

    if jq_filter is None:
        assert not m_jq.compile.called
        assert not m_str.called
        return
    assert (
        m_jq.compile.call_args
        == [(jq_filter,), {}])
    assert (
        m_jq.compile.return_value.input_text.call_args
        == [(json_str,), {}])
    assert (
        m_str.call_args
        == [((m_jq.compile.return_value
                  .input_text.return_value
                  .text.return_value),), {}])
