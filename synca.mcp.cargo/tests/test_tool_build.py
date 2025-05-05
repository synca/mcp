"""Isolated tests for synca.mcp.cargo.tool.build."""

from unittest.mock import MagicMock

import pytest

from synca.mcp.cargo.tool.base import CargoTool
from synca.mcp.cargo.tool.build import BuildTool


def test_tool_build_constructor():
    """Test BuildTool class initialization."""
    ctx = MagicMock()
    path = MagicMock()
    args = MagicMock()
    tool = BuildTool(ctx, path, args)
    assert isinstance(tool, BuildTool)
    assert isinstance(tool, CargoTool)
    assert tool.ctx == ctx
    assert tool._path_str == path
    assert tool.tool_name == "build"
    assert "tool_name" not in tool.__dict__
    assert tool._args == args


@pytest.mark.parametrize("return_code", [0, 1, None])
@pytest.mark.parametrize("has_finished", [True, False])
@pytest.mark.parametrize("warnings", [[], ["warning: unused"]])
@pytest.mark.parametrize("errors", [[], ["error: type mismatch"]])
@pytest.mark.parametrize("notes", [[], ["note: consider adding this"]])
@pytest.mark.parametrize("mode", [None, "debug", "release"])
@pytest.mark.parametrize("timing", [None, {"total": "1.23s"}])
@pytest.mark.parametrize(
    "statuses", [None, {"crate": {"status": "compiling", "version": None}}])
def test_build_parse_output(
        patches, return_code, has_finished, warnings, errors, notes,
        mode, timing, statuses):
    ctx = MagicMock()
    path = MagicMock()
    args = MagicMock()
    tool = BuildTool(ctx, path, args)
    stdout = "stdout content"
    stderr = "stderr content"
    if has_finished:
        stdout = "Finished dev [unoptimized + debuginfo]\n" + stdout
    combined_output = stdout + "\n" + stderr
    successful = return_code == 0 and has_finished
    expected_output = (
        ""
        if (successful and not warnings and not errors)
        else combined_output)
    expected_issues = len(warnings) + len(errors)
    message = (
        "Build completed successfully with no issues"
        if (successful and not warnings and not errors)
        else f"Build issues: {expected_issues}")
    expected_info = {}
    if mode:
        expected_info["mode"] = mode
    if timing:
        expected_info["timing"] = timing
    if statuses:
        expected_info["statuses"] = statuses
    if warnings:
        expected_info["warnings_count"] = len(warnings)
        expected_info["warnings"] = warnings
    if errors:
        expected_info["errors_count"] = len(errors)
        expected_info["errors"] = errors
    if notes:
        expected_info["notes"] = notes
    patched = patches(
        "BuildTool.parse_issues",
        "BuildTool._extract_mode",
        "BuildTool._extract_timing",
        "BuildTool._extract_target_statuses",
        prefix="synca.mcp.cargo.tool.build")

    with patched as (m_parse_issues, m_mode, m_timing, m_statuses):
        m_parse_issues.return_value = (warnings, errors, notes)
        m_mode.return_value = mode
        m_timing.return_value = timing
        m_statuses.return_value = statuses
        assert (
            tool.parse_output(stdout, stderr, return_code)
            == (return_code,
                message,
                expected_output,
                expected_info))

    assert (
        m_parse_issues.call_args
        == [(combined_output,), {}])
    assert (
        m_mode.call_args
        == [(combined_output,), {}])
    assert (
        m_timing.call_args
        == [(combined_output,), {}])
    assert (
        m_statuses.call_args
        == [(combined_output,), {}])


@pytest.mark.parametrize(
    "combined_output,expected",
    [("",
      None),
     ("Finished dev [unoptimized + debuginfo]",
      "debug"),
     ("Finished test [unoptimized + debuginfo]",
      "debug"),
     ("Finished release [optimized]",
      "release"),
     ("Compiling foo v0.1.0\n"
      "Finished dev [unoptimized + debuginfo]\n"
      "Running `target/debug/foo`",
      "debug"),
     ("Compiling foo v0.1.0\n"
      "Finished release [optimized]\n"
      "Running `target/release/foo`",
      "release"),
     ("Compiling foo v0.1.0\n"
      "error: mismatched types",
      None)])
def test_extract_mode(combined_output, expected):
    """Test _extract_mode correctly identifies debug/release mode."""
    ctx = MagicMock()
    path = MagicMock()
    args = MagicMock()
    tool = BuildTool(ctx, path, args)
    assert (
        tool._extract_mode(combined_output)
        == expected)


@pytest.mark.parametrize(
    "combined_output,line_args",
    [("", []),
     ("Compiling foo v0.1.0", []),
     ("Finished dev [unoptimized + debuginfo] in 2.35s",
      ["Finished dev [unoptimized + debuginfo] in 2.35s"]),
     ("Compiling foo v0.1.0\n"
      "Finished release [optimized] in 3.47s\n"
      "Running `target/release/foo`",
      ["Finished release [optimized] in 3.47s"]),
     ("Compiling foo v0.1.0\n"
      "Finished test [unoptimized + debuginfo] in 1.23s\n"
      "Finished bench [optimized] in 0.89s",
      ["Finished test [unoptimized + debuginfo] in 1.23s",
       "Finished bench [optimized] in 0.89s"])])
@pytest.mark.parametrize(
    "status_return",
    [None, MagicMock()])
def test_extract_timing(patches, combined_output, line_args, status_return):
    """Test _extract_timing extracts timing information correctly."""
    ctx = MagicMock()
    path = MagicMock()
    args = MagicMock()
    tool = BuildTool(ctx, path, args)
    patched = patches(
        "BuildTool._status_finished",
        prefix="synca.mcp.cargo.tool.build")

    with patched as (m_status_finished,):
        m_status_finished.return_value = status_return
        assert (
            tool._extract_timing(combined_output)
            == ({"total": status_return}
                if (status_return is not None
                    and line_args)
                else dict(total="")))

    if status_return is None:
        expected_call_args = [
            ((line,),)
            for line
            in line_args]
    else:
        expected_call_args = (
            [((line_args[0],),)]
            if line_args
            else [])
    assert (
        m_status_finished.call_args_list
        == expected_call_args)


@pytest.mark.parametrize(
    "error",
    [None,
     IndexError,
     ValueError,
     BaseException])
@pytest.mark.parametrize("finished", [False, True])
def test_status_finished(error, finished):
    """Test _status_finished correctly extracts timing information
    and handles exceptions.
    """
    ctx = MagicMock()
    path = MagicMock()
    args = MagicMock()
    tool = BuildTool(ctx, path, args)
    line = MagicMock()
    time_part = (
        line.split.return_value
            .__getitem__.return_value
            .strip.return_value)
    time_part.endswith.return_value = finished
    if error:
        line.split.side_effect = error("Test error")

    if error and error not in [IndexError, ValueError]:
        with pytest.raises(error) as e:
            tool._status_finished(line)
    else:
        assert (
            tool._status_finished(line)
            == (time_part
                if (finished and not error)
                else None))

    assert (
        line.split.call_args
        == [("in ",), {}])
    if error:
        assert not line.split.return_value.__getitem__.called
        if error not in [IndexError, ValueError]:
            assert str(e.value) == "Test error"
        return
    assert (
        line.split.return_value.__getitem__.call_args
        == [(-1,), {}])
    assert (
        line.split.return_value.__getitem__.return_value.strip.call_args
        == [(), {}])
    assert (
        time_part.endswith.call_args
        == [("s",), {}])


@pytest.mark.parametrize(
    "combined_output,expected",
    [("",
      None),
     ("Compiling foo v0.1.0",
      {"foo": {"status": "compiling", "version": "v0.1.0"}}),
     ("Compiling bar",
      {"bar": {"status": "compiling", "version": None}}),
     ("Fresh baz v0.2.0",
      {"baz": {"status": "fresh", "version": "v0.2.0"}}),
     ("Compiling foo v0.1.0\n"
      "Fresh bar v0.2.0\n"
      "Compiling baz",
      {"foo": {"status": "compiling", "version": "v0.1.0"},
       "bar": {"status": "fresh", "version": "v0.2.0"},
       "baz": {"status": "compiling", "version": None}}),
     ("Random output\n"
      "error: mismatched types",
      None)])
def test_extract_target_statuses(patches, combined_output, expected):
    """Test _extract_target_statuses extracts compilation status correctly."""
    ctx = MagicMock()
    path = MagicMock()
    args = MagicMock()
    tool = BuildTool(ctx, path, args)
    patched = patches(
        "BuildTool._status_compiling",
        "BuildTool._status_fresh",
        prefix="synca.mcp.cargo.tool.build")

    with patched as (m_compiling, m_fresh):
        def mock_status(line, prefix, status):
            if not line.startswith(prefix):
                return None
            parts = line.split(prefix)[1].strip().split(" ")
            if not parts or not parts[0]:
                return None
            status_dict = {
                "status": status,
                "version": parts[1] if len(parts) > 1 else None
            }
            return (parts[0], status_dict)

        m_compiling.side_effect = lambda line: mock_status(
            line, "Compiling ", "compiling")
        m_fresh.side_effect = lambda line: mock_status(
            line, "Fresh ", "fresh")

        result = tool._extract_target_statuses(combined_output)
        assert result == expected

        compiling_calls = [
            ((line,), {})
            for line in combined_output.splitlines()
            if line.startswith("Compiling ")]
        fresh_calls = [
            ((line,), {})
            for line in combined_output.splitlines()
            if line.startswith("Fresh ")]

        assert m_compiling.call_args_list == compiling_calls
        assert m_fresh.call_args_list == fresh_calls


@pytest.mark.parametrize("error", [None, IndexError, ValueError])
@pytest.mark.parametrize("parts_len", [0, 1, 2])
def test_status_compiling(error, parts_len):
    """Test _status_compiling extracts compiling status correctly."""
    ctx = MagicMock()
    path = MagicMock()
    args = MagicMock()
    tool = BuildTool(ctx, path, args)
    line = MagicMock()
    if error:
        line.split.side_effect = error("Test error")
    parts = (
        line.split.return_value
        .__getitem__.return_value
        .strip.return_value
        .split.return_value)
    parts.__len__.return_value = parts_len
    expected = {"status": "compiling"}
    if parts_len > 1:
        expected["version"] = parts.__getitem__.return_value

    assert (
        tool._status_compiling(line)
        == (None
            if (error or parts_len < 1)
            else (parts.__getitem__.return_value,
                  expected)))

    assert (
        line.split.call_args
        == [("Compiling ",), {}])
    if error:
        assert not line.split.return_value.__getitem__.called
        return
    assert (
        line.split.return_value.__getitem__.call_args
        == [(1, ), {}])
    assert (
        line.split.return_value.__getitem__.return_value.strip.call_args
        == [(), {}])
    assert (
        (line.split.return_value
             .__getitem__.return_value
             .strip.return_value
             .split.call_args)
        == [(" ",), {}])
    assert (
        parts.__len__.call_args_list
        == ([[(), {}], [(), {}]]
            if parts_len > 0
            else [[(), {}]]))
    if not parts_len > 0:
        assert not parts.__getitem__.called
        return
    assert (
        parts.__getitem__.call_args_list
        == ([[(1,), {}], [(0,), {}]]
            if parts_len > 1
            else [[(0,), {}]]))


@pytest.mark.parametrize("error", [None, IndexError, ValueError])
@pytest.mark.parametrize("parts_len", [0, 1, 2])
def test_status_fresh(error, parts_len):
    """Test _status_fresh extracts fresh status correctly."""
    ctx = MagicMock()
    path = MagicMock()
    args = MagicMock()
    tool = BuildTool(ctx, path, args)
    line = MagicMock()
    if error:
        line.split.side_effect = error("Test error")
    parts = (
        line.split.return_value
        .__getitem__.return_value
        .strip.return_value
        .split.return_value)
    parts.__len__.return_value = parts_len
    expected = {"status": "fresh"}
    if parts_len > 1:
        expected["version"] = parts.__getitem__.return_value

    assert (
        tool._status_fresh(line)
        == (None
            if (error or parts_len < 1)
            else (parts.__getitem__.return_value,
                  expected)))

    assert (
        line.split.call_args
        == [("Fresh ",), {}])
    if error:
        assert not line.split.return_value.__getitem__.called
        return
    assert (
        line.split.return_value.__getitem__.call_args
        == [(1, ), {}])
    assert (
        line.split.return_value.__getitem__.return_value.strip.call_args
        == [(), {}])
    assert (
        (line.split.return_value
             .__getitem__.return_value
             .strip.return_value
             .split.call_args)
        == [(" ",), {}])
    assert (
        parts.__len__.call_args_list
        == ([[(), {}], [(), {}]]
            if parts_len > 0
            else [[(), {}]]))
    if not parts_len > 0:
        assert not parts.__getitem__.called
        return
    assert (
        parts.__getitem__.call_args_list
        == ([[(1,), {}], [(0,), {}]]
            if parts_len > 1
            else [[(0,), {}]]))
