"""Isolated tests for synca.mcp.cargo.tool.run."""

from unittest.mock import MagicMock

import pytest

from synca.mcp.cargo.tool.base import CargoTool
from synca.mcp.cargo.tool.run import RunTool


def test_tool_run_constructor():
    """Test RunTool class initialization."""
    ctx = MagicMock()
    path = MagicMock()
    tool = RunTool(ctx, path)
    assert isinstance(tool, RunTool)
    assert isinstance(tool, CargoTool)
    assert tool.ctx == ctx
    assert tool._path_str == path
    assert tool.tool_name == "run"
    assert "tool_name" not in tool.__dict__


@pytest.mark.parametrize("return_code", [0, 1, None])
@pytest.mark.parametrize("has_finished", [True, False])
@pytest.mark.parametrize("has_running_line", [True, False])
@pytest.mark.parametrize("warnings", [[], ["warning: unused variable"]])
@pytest.mark.parametrize("errors", [[], ["error: mismatched types"]])
@pytest.mark.parametrize("compilation_errors", [True, False])
@pytest.mark.parametrize("notes", [[], ["note: consider adding this"]])
@pytest.mark.parametrize("binary_name", [None, "test-binary"])
@pytest.mark.parametrize("build_mode", [None, "debug", "release"])
def test_run_parse_output(
        patches, return_code, has_finished, has_running_line, warnings,
        errors, compilation_errors, notes, binary_name, build_mode):
    """Test RunTool.parse_output method with various combinations of inputs."""
    ctx = MagicMock()
    path = MagicMock()
    tool = RunTool(ctx, path)
    stdout = "Program output here\n"
    if has_finished:
        stdout += "Finished dev [unoptimized + debuginfo]\n"
    if has_running_line:
        stdout += "Running `target/debug/some-binary`\n"
    stderr = ""
    combined_output = stdout + "\n" + stderr
    mock_compilation_output = (
        "Compilation output here"
        if has_running_line
        else None)
    mock_program_output = "Program output here"
    issues_count = len(warnings) + len(errors)
    successful = return_code == 0 and not issues_count
    error_type = (
        "compilation"
        if compilation_errors and errors
        else ("runtime"
              if errors
              else None))
    expected_message = (
        "Program executed successfully"
        if successful
        else ("Failed to compile the program"
              if error_type == "compilation"
              else "Program execution failed"))
    expected_output = (
        ""
        if successful
        else combined_output)
    expected_info = {"mode": build_mode or "debug"}
    if binary_name:
        expected_info["artifact_path"] = binary_name
    if mock_compilation_output:
        expected_info["compilation_output"] = mock_compilation_output
    if mock_program_output:
        expected_info["program_output"] = mock_program_output
    if warnings:
        expected_info["warnings_count"] = len(warnings)
        expected_info["warnings"] = warnings
    if errors:
        expected_info["errors_count"] = len(errors)
        expected_info["errors"] = errors
        expected_info["error_types"] = {error_type: 1}
    if notes:
        expected_info["notes"] = notes
    patched = patches(
        "RunTool.parse_issues",
        "RunTool._extract_all",
        "RunTool._determine_error_type",
        prefix="synca.mcp.cargo.tool.run")

    with patched as (m_parse_issues, m_extract_all, m_determine_error_type):
        m_parse_issues.return_value = (warnings, errors, notes)
        m_extract_all.return_value = (
            build_mode,
            binary_name,
            mock_compilation_output,
            mock_program_output)
        if errors:
            m_determine_error_type.return_value = error_type
        assert (
            tool.parse_output(stdout, stderr, return_code)
            == (return_code or 0,
                expected_message,
                expected_output,
                expected_info))

    assert (
        m_parse_issues.call_args
        == [(combined_output,), {}])
    assert (
        m_extract_all.call_args
        == [(combined_output,), {}])
    if errors:
        assert (
            m_determine_error_type.call_args
            == [(errors,), {}])
    else:
        assert not m_determine_error_type.called


@pytest.mark.parametrize("dev_match", [True, False])
@pytest.mark.parametrize("release_match", [True, False])
@pytest.mark.parametrize("test_match", [True, False])
def test_extract_build_mode_from_line(dev_match, release_match, test_match):
    """Test _extract_build_mode_from_line correctly identifies build modes."""
    ctx = MagicMock()
    path = MagicMock()
    tool = RunTool(ctx, path)
    line = MagicMock()
    line.__contains__.side_effect = lambda x: (
        dev_match if x == "Finished dev" else
        release_match if x == "Finished release" else
        test_match if x == "Finished test" else
        False)
    expected = (
        "debug"
        if dev_match or test_match
        else ("release"
              if release_match
              else None))
    assert (
        tool._extract_build_mode_from_line(line)
        == expected)
    if dev_match:
        assert (
            line.__contains__.call_args_list
            == [(("Finished dev",), {})])
    elif test_match:
        assert (
            line.__contains__.call_args_list
            == [(("Finished dev",), {}),
                (("Finished test",), {})])
    elif release_match:
        assert (
            line.__contains__.call_args_list
            == [(("Finished dev",), {}),
                (("Finished test",), {}),
                (("Finished release",), {})])
    else:
        assert (
            line.__contains__.call_args_list
            == [(("Finished dev",), {}),
                (("Finished test",), {}),
                (("Finished release",), {})])


@pytest.mark.parametrize(
    "running_text,target_text,expected",
    [(True, True, "test-binary"),
     (True, False, None),
     (False, True, None),
     (False, False, None)])
@pytest.mark.parametrize(
    "error",
    [None,
     ValueError,
     IndexError,
     BaseException])
def test_extract_binary_name_from_line(
        patches, running_text, target_text, expected, error):
    """Test _extract_binary_name_from_line extracts binary names correctly."""
    ctx = MagicMock()
    path = MagicMock()
    tool = RunTool(ctx, path)
    line = MagicMock()
    line.__contains__.side_effect = lambda x: (
        running_text if x == "Running `" else
        target_text if x == "target" else
        False)
    parts_mock = MagicMock()
    parts_mock.split.return_value = ["test-binary"]
    if running_text and target_text and error is None:
        line.split.return_value = ['', parts_mock]
    elif running_text and target_text:
        # Only set exception for cases where split would be called
        line.split.side_effect = error("Test error")
    # BaseException should only raise when we actually call split
    if error is BaseException and running_text and target_text:
        with pytest.raises(BaseException):
            tool._extract_binary_name_from_line(line)
        return
    actual_expected = (
        None
        if (error and running_text and target_text)
        else expected)
    assert (
        tool._extract_binary_name_from_line(line)
        == actual_expected)
    assert (
        line.__contains__.call_args_list[0]
        == (("Running `",), {}))
    if running_text:
        assert (
            line.__contains__.call_args_list[1]
            == (("target",), {}))
        if target_text:
            assert (
                line.split.call_args
                == [('`',), {}])
            if error is None:
                parts = line.split.return_value[1]
                assert (
                    parts.split.call_args
                    == [(), {}])


@pytest.mark.parametrize(
    "build_mode,binary_name",
    [(None, None),
     ("debug", None),
     ("release", None),
     (None, "test-binary"),
     ("debug", "test-binary"),
     ("release", "test-binary")])
@pytest.mark.parametrize(
    "has_running_line",
    [True, False])
@pytest.mark.parametrize(
    "output_content",
    ["", "Program output here"])
def test_extract_all(
        patches, build_mode, binary_name, has_running_line, output_content):
    """Test _extract_all method extracts metadata from output correctly."""
    ctx = MagicMock()
    path = MagicMock()
    tool = RunTool(ctx, path)
    lines = [output_content] if output_content else []
    if has_running_line:
        running_line = "Running `target/debug/some-binary`"
        lines.append(running_line)
    if build_mode == "debug":
        lines.append("Finished dev [unoptimized + debuginfo]")
    elif build_mode == "release":
        lines.append("Finished release [optimized]")
    combined_output = "\n".join(lines)
    running_line_idx = (
        lines.index(running_line)
        if has_running_line
        else None)
    compilation_output = (
        "\n".join(lines[:running_line_idx+1])
        if has_running_line
        else None)
    program_output = (
        "\n".join(lines[running_line_idx+1:])
        if has_running_line and running_line_idx + 1 < len(lines)
        else (combined_output
              if (output_content
                  or not has_running_line)
              else None))
    expected_binary = (
        binary_name
        if has_running_line
        else None)
    expected_result = (
        build_mode,
        expected_binary,
        (compilation_output
         if (compilation_output
             and compilation_output.strip())
         else None),
        (program_output
         if (program_output
             and program_output.strip())
         else combined_output))
    patched = patches(
        "RunTool._extract_build_mode_from_line",
        "RunTool._extract_binary_name_from_line",
        "RunTool._split_outputs",
        prefix="synca.mcp.cargo.tool.run")
    with patched as (m_extract_mode, m_extract_binary, m_split_outputs):
        m_extract_mode.side_effect = lambda line: (
            build_mode
            if build_mode == "debug" and "Finished dev" in line
            else (build_mode
                  if build_mode == "release" and "Finished release" in line
                  else None))
        m_extract_binary.return_value = (
            binary_name
            if has_running_line
            else None)
        m_split_outputs.return_value = (
            (compilation_output
             if (compilation_output
                 and compilation_output.strip())
             else None),
            (program_output
             if (program_output
                 and program_output.strip())
             else combined_output))
        assert (
            tool._extract_all(combined_output)
            == expected_result)
    expected_extract_mode_calls = []
    for line in lines:
        expected_extract_mode_calls.append(((line,), {}))
    assert (
        m_extract_mode.call_args_list
        == expected_extract_mode_calls)
    expected_extract_binary_calls = []
    if has_running_line:
        expected_extract_binary_calls.append(((running_line,), {}))
    assert (
        m_extract_binary.call_args_list
        == expected_extract_binary_calls)
    assert (
        m_split_outputs.call_args
        == [(lines, running_line_idx, combined_output), {}])


@pytest.mark.parametrize(
    "running_line_idx",
    [None, 0, 1, 2])
@pytest.mark.parametrize(
    "lines,expected_compilation,expected_program",
    [([], None, ""),
     (["line1"], None, "line1"),
     (["line1", "line2"], "line1", "line2"),
     (["line1", "line2", "line3"], "line1\nline2", "line3"),
     (["   "], None, "   ")])
def test_split_outputs(
        running_line_idx, lines, expected_compilation, expected_program):
    """Test _split_outputs correctly separates compilation and
    program outputs.
    """
    ctx = MagicMock()
    path = MagicMock()
    tool = RunTool(ctx, path)
    if running_line_idx is None:
        expected_compilation = None
        expected_program = "\n".join(lines)
    elif running_line_idx >= len(lines):
        # If index is out of bounds, both should be empty
        expected_compilation = (
            "\n".join(lines[:running_line_idx+1])
            if lines
            else None)
        expected_program = ""
    else:
        expected_compilation = "\n".join(lines[:running_line_idx+1])
        expected_program = (
            "\n".join(lines[running_line_idx+1:])
            or "\n".join(lines))
    if expected_compilation == "":
        expected_compilation = None
    if expected_compilation and not expected_compilation.strip():
        expected_compilation = None
    combined_output = "\n".join(lines)

    assert (
        tool._split_outputs(lines, running_line_idx, combined_output)
        == (expected_compilation,
            expected_program or combined_output))


@pytest.mark.parametrize(
    "errors,expected_type",
    [([""], "runtime"),
     ([], "runtime"),
     (["error: mismatched types"],
      "runtime"),
     (["error: could not compile"],
      "compilation"),
     (["error: could not compile `myproject`"],
      "compilation"),
     (["error: attribute not found", "error: could not compile this project"],
      "compilation"),
     (["error: unresolved import"],
      "runtime"),
     (["warning: this is not actually an error", "note: consider this"],
      "runtime"),
     (["error: COULD NOT COMPILE"], "compilation"),
     (["error with some other text",
       "error: Could not compile due to previous error"],
      "compilation")])
def test_determine_error_type(errors, expected_type):
    """Test _determine_error_type correctly identifies error types."""
    ctx = MagicMock()
    path = MagicMock()
    tool = RunTool(ctx, path)

    assert (
        tool._determine_error_type(errors)
        == expected_type)
