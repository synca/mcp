"""Isolated tests for synca.mcp.cargo.__main__."""

import runpy

import pytest


@pytest.mark.parametrize("ismain", [True, False])
def test_main_import(patches, ismain):
    """Test that mcp.run() is not called during normal import."""
    patched = patches(
        "mcp",
        prefix="synca.mcp.cargo.server")
    name = (
        "__main__"
        if ismain
        else "__NOT_main__")

    with patched as (m_mcp, ):
        runpy.run_module("synca.mcp.cargo.__main__", run_name=name)

    if not ismain:
        assert not m_mcp.run.called
        return
    assert (
        m_mcp.run.call_args
        == [(), {}])
