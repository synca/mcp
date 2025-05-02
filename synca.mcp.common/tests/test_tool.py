"""Isolated tests for synca.mcp.common.tool."""

import pytest
from unittest.mock import AsyncMock, MagicMock, PropertyMock

from synca.mcp.common.tool import CLITool, Tool


@pytest.mark.asyncio
async def test_tool_constructor():
    """Test Tool class initialization."""
    ctx = MagicMock()
    tool = Tool(ctx)
    assert tool.ctx == ctx
    with pytest.raises(NotImplementedError):
        tool.tool_name
    with pytest.raises(NotImplementedError):
        tool.command()
        breakpoint()
    with pytest.raises(NotImplementedError):
        await tool.execute(MagicMock())
    with pytest.raises(NotImplementedError):
        await tool.parse_output(
            MagicMock(),
            MagicMock(),
            MagicMock())


@pytest.mark.parametrize("args", [None, ["--ignore=E501"]])
@pytest.mark.asyncio
async def test_tool_handle(patches, args):
    """Test handle method with various parameters."""
    ctx = MagicMock()
    tool = Tool(ctx)
    patched = patches(
        "Tool.command",
        "Tool.execute",
        "Tool.parse_output",
        "Tool.response",
        prefix="synca.mcp.common.tool")

    with patched as (m_build, m_exec, m_parse, m_format):
        m_exec.return_value = (MagicMock(), MagicMock(), MagicMock())
        m_parse.return_value = (
            MagicMock(), MagicMock(), MagicMock(), MagicMock())
        assert (
            await tool.handle(args)
            == m_format.return_value)

    assert (
        m_build.call_args
        == [(args, ), {}])
    assert (
        m_exec.call_args
        == [(m_build.return_value, ), {}])
    assert (
        m_parse.call_args
        == [m_exec.return_value, {}])
    assert (
        m_format.call_args
        == [m_parse.return_value, {}])


def test_tool_parse_output(patches):
    """Test parse_output method."""
    ctx = MagicMock()
    tool = Tool(ctx)
    with pytest.raises(NotImplementedError):
        tool.parse_output(
            MagicMock(), MagicMock(), MagicMock())


def test_tool_response(patches):
    """Test response method with parametrized inputs."""
    ctx = MagicMock()
    output = MagicMock()
    tool = Tool(ctx)
    info = MagicMock()
    return_code = MagicMock()
    message = MagicMock()
    assert (
        tool.response(return_code, message, output, info)
        == {
            "data": {
                "return_code": return_code,
                "message": message,
                "output": output,
                "info": info,
            }})


@pytest.mark.parametrize(
    "error",
    [None,
     BaseException])
@pytest.mark.parametrize(
    "args",
    [(MagicMock(),),
     (MagicMock(), MagicMock()),
     ()])
@pytest.mark.parametrize(
    "kwargs",
    [{"args": ["--check"], "verbose": False},
     {"verbose": True},
     {}])
@pytest.mark.asyncio
async def test_tool_run(patches, iters, args, kwargs, error):
    """Test run() with parametrized arguments."""
    ctx = MagicMock()
    tool = Tool(ctx)
    tool.__class__.__name__ = "CustomTool"
    patched = patches(
        "traceback",
        "Tool.handle",
        prefix="synca.mcp.common.tool")

    with patched as (m_tb, m_handle):
        if error:
            m_handle.side_effect = error("Test error")
        assert (
            await tool.run(*args, **kwargs)
            == (m_handle.return_value
                if not error
                else dict(
                    error=(
                        "Failed to run custom: Test error\n"
                        f"{m_tb.format_exc.return_value}"))))

    assert (
        m_handle.call_args
        == [args, kwargs])
    if error:
        assert (
            m_tb.format_exc.call_args
            == [(), {}])
        return
    assert not m_tb.format_exc.called


# CLITool

def test_cli_tool_constructor():
    """Test Tool class initialization."""
    ctx = MagicMock()
    path = MagicMock()
    tool = CLITool(ctx, path)
    assert isinstance(tool, Tool)
    assert tool.ctx == ctx
    assert tool._path_str == path
    with pytest.raises(NotImplementedError):
        tool.tool_name


def test_cli_tool_path(patches):
    """Test Tool path."""
    ctx = MagicMock()
    path = MagicMock()
    tool = CLITool(ctx, path)
    patched = patches(
        ("Tool.tool_name",
         dict(new_callable=PropertyMock)),
        prefix="synca.mcp.common.tool")

    with patched as (m_name, ):
        assert (
            tool.tool_path
            == m_name.return_value)


def test_cli_tool_tool_path(patches):
    """Test Tool path."""
    ctx = MagicMock()
    path = MagicMock()
    tool = CLITool(ctx, path)
    patched = patches(
        "pathlib",
        "CLITool.validate_path",
        prefix="synca.mcp.common.tool")

    with patched as (m_path, m_valid):
        assert (
            tool.path
            == m_path.Path.return_value)

    assert (
        m_path.Path.call_args
        == [(path, ), {}])
    assert (
        m_valid.call_args
        == [(m_path.Path.return_value, ), {}])
    assert "path" in tool.__dict__


@pytest.mark.parametrize(
    "args",
    [None,
     [MagicMock()],
     [MagicMock(), MagicMock()]])
def test_cli_tool_command(patches, args):
    """Test command with parametrized arguments."""
    path = "/test/path"
    ctx = MagicMock()
    path = MagicMock()
    tool = CLITool(ctx, path)
    patched = patches(
        ("CLITool.tool_path",
         dict(new_callable=PropertyMock)),
        prefix="synca.mcp.common.tool")

    with patched as (m_tool_path, ):
        assert (
            tool.command(args)
            == (m_tool_path.return_value, *(args or [])))

    assert "tool_path" not in tool.__dict__


@pytest.mark.asyncio
async def test_cli_tool_execute(patches):
    """Test execute method."""
    cmd = (MagicMock(), MagicMock(), MagicMock())
    ctx = MagicMock()
    path = MagicMock()
    tool = CLITool(ctx, path)
    stdout = MagicMock()
    stderr = MagicMock()
    patched = patches(
        "asyncio",
        "str",
        ("CLITool.path",
         dict(new_callable=PropertyMock)),
        prefix="synca.mcp.common.tool")

    with patched as (m_aio, m_str, m_path):
        m_subproc = m_aio.create_subprocess_exec = AsyncMock()
        proc = m_subproc.return_value
        proc.communicate.return_value = (stdout, stderr)
        assert (
            await tool.execute(cmd)
            == (stdout.decode.return_value,
                stderr.decode.return_value,
                proc.returncode))

    assert (
        m_subproc.call_args
        == [cmd,
            dict(
                cwd=m_str.return_value,
                stdout=m_aio.subprocess.PIPE,
                stderr=m_aio.subprocess.PIPE)])
    assert (
        m_str.call_args
        == [(m_path.return_value, ), {}])


@pytest.mark.parametrize(
    "exists",
    [True, False])
@pytest.mark.parametrize(
    "is_dir",
    [True, False])
def test_cli_tool_validate_path(patches, exists, is_dir):
    """Test validate_path with parametrized existence and directory check."""
    patched = patches(
        "pathlib.Path",
        prefix="synca.mcp.common.tool")
    ctx = MagicMock()
    path = MagicMock()
    tool = CLITool(ctx, path)

    with patched as (m_path, ):
        m_path.return_value.exists.return_value = exists
        m_path.return_value.is_dir.return_value = is_dir
        if not exists:
            with pytest.raises(FileNotFoundError) as e:
                tool.validate_path(path)
        elif not is_dir:
            with pytest.raises(NotADirectoryError) as e:
                tool.validate_path(path)
        else:
            assert not tool.validate_path(path)

    assert m_path.call_args == [(path,), {}]
    assert m_path.return_value.exists.called
    assert (
        m_path.return_value.is_dir.called
        == exists)
    if not exists:
        assert (
            e.value.args[0]
            == f"Path '{path}' does not exist")
    elif not is_dir:
        assert (
            e.value.args[0]
            == f"Path '{path}' is not a directory")
