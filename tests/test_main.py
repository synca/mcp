"""Isolated tests for snake.mcp.server.__main__."""

import runpy

import pytest


@pytest.mark.parametrize("ismain", [True, False])
def test_main_import(patches, ismain):
    """Test that mcp.run() is not called during normal import."""
    patched = patches(
        "mcp",
        prefix="snake.mcp.server.server")
    name = (
        "__main__"
        if ismain
        else "__NOT_main__")

    with patched as (m_mpc, ):
        runpy.run_module("snake.mcp.server.__main__", run_name=name)

    if not ismain:
        assert not m_mpc.run.called
        return
    assert (
        m_mpc.run.call_args
        == [(), {}])
