"""Isolated tests for synca.mcp.cargo.tool.doc."""

from unittest.mock import MagicMock

import pytest

from synca.mcp.cargo.tool.base import CargoTool
from synca.mcp.cargo.tool.doc import DocTool


def test_tool_doc_constructor():
    """Test DocTool class initialization."""
    ctx = MagicMock()
    path = MagicMock()
    tool = DocTool(ctx, path)
    assert isinstance(tool, DocTool)
    assert isinstance(tool, CargoTool)
    assert tool.ctx == ctx
    assert tool._path_str == path
    assert tool.tool_name == "doc"
    assert "tool_name" not in tool.__dict__


@pytest.mark.parametrize("return_code", [0, 1, None])
@pytest.mark.parametrize("has_finished", [True, False])
@pytest.mark.parametrize("warnings", [[], ["warning: unused doc comment"]])
@pytest.mark.parametrize("errors", [[], ["error: failed to generate docs"]])
@pytest.mark.parametrize("notes", [[], ["note: consider adding docstrings"]])
@pytest.mark.parametrize("package_name", [None, "test-package"])
def test_doc_parse_output(
        patches, return_code, has_finished, warnings, errors,
        notes, package_name):
    """Test the parse_output method for DocTool."""
    ctx = MagicMock()
    path = MagicMock()
    tool = DocTool(ctx, path)
    stdout = "stdout content"
    stderr = "stderr content"
    if has_finished:
        stdout = "Finished dev [unoptimized + debuginfo]\n" + stdout
    combined_output = stdout + "\n" + stderr
    # Mock path for doc path
    mock_path = MagicMock()
    mock_path.__truediv__.return_value = mock_path
    tool.path = mock_path
    mock_path.__str__.return_value = "/mocked/path"
    issues_count = len(warnings) + len(errors)
    successful = return_code == 0 and has_finished
    expected_output = (
        ""
        if (successful and not issues_count)
        else combined_output)
    message = (
        "Documentation successfully generated"
        if (successful and not issues_count)
        else "Documentation generation failed")
    expected_info = {}
    if package_name:
        expected_info["artifact_path"] = "/mocked/path"
    if warnings:
        expected_info["warnings_count"] = len(warnings)
        expected_info["warnings"] = warnings
    if errors:
        expected_info["errors_count"] = len(errors)
        expected_info["errors"] = errors
    if notes:
        expected_info["notes"] = notes

    patched = patches(
        "DocTool.parse_issues",
        "DocTool._extract_package_name",
        prefix="synca.mcp.cargo.tool.doc")

    with patched as (m_parse_issues, m_extract_package_name):
        m_parse_issues.return_value = (warnings, errors, notes)
        m_extract_package_name.return_value = package_name
        assert (
            tool.parse_output(stdout, stderr, return_code)
            == (return_code or 0,
                message,
                expected_output,
                expected_info))

    assert (
        m_parse_issues.call_args
        == [(combined_output,), {}])
    assert (
        m_extract_package_name.call_args
        == [(), {}])


@pytest.mark.parametrize(
    "content,expected",
    [("name = \"package-name\"\nversion = \"0.1.0\"",
      "package-name"),
     ("name = 'package-name'\nversion = \"0.1.0\"",
      "package-name"),
     ("name   =    \"package-name\"   \nversion = \"0.1.0\"",
      "package-name"),
     ("name=\"no-spaces\"\nversion = \"0.1.0\"",
      "no-spaces"),
     ("# No name field\nversion = \"0.1.0\"",
      None)])
def test_doc_extract_package_name(patches, content, expected):
    """Test _extract_package_name extracts the package name from Cargo.toml."""
    ctx = MagicMock()
    path = MagicMock()
    tool = DocTool(ctx, path)
    mock_path = MagicMock()
    tool.path = mock_path
    mock_cargo_toml = MagicMock()
    mock_path.__truediv__.return_value = mock_cargo_toml
    mock_cargo_toml.read_text.return_value = content
    assert tool._extract_package_name() == expected
    assert (
        mock_path.__truediv__.call_args
        == [("Cargo.toml",), {}])
    assert (
        mock_cargo_toml.read_text.call_args
        == [(), {}])
