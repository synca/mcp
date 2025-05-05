
import pytest
from unittest.mock import AsyncMock, MagicMock, PropertyMock

from synca.mcp.common.tool import CLITool, Tool


# CLITool

def test_cli_tool_constructor():
    """Test Tool class initialization."""
    ctx = MagicMock()
    path = MagicMock()
    args = MagicMock()
    tool = CLITool(ctx, path, args)
    assert isinstance(tool, Tool)
    assert tool.ctx == ctx
    assert tool._path_str == path
    assert tool._args == args
    assert tool.args == args
    assert "args" not in tool.__dict__
    with pytest.raises(NotImplementedError):
        tool.tool_name


def test_cli_tool_path(patches):
    """Test Tool path."""
    ctx = MagicMock()
    path = MagicMock()
    args = MagicMock()
    tool = CLITool(ctx, path, args)
    patched = patches(
        "pathlib",
        "CLITool.validate_path",
        prefix="synca.mcp.common.tool.cli")

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


def test_cli_tool_tool_path(patches):
    """Test Tool path."""
    ctx = MagicMock()
    path = MagicMock()
    args = MagicMock()
    tool = CLITool(ctx, path, args)
    patched = patches(
        ("Tool.tool_name",
         dict(new_callable=PropertyMock)),
        prefix="synca.mcp.common.tool.cli")

    with patched as (m_name, ):
        assert (
            tool.tool_path
            == m_name.return_value)


def test_cli_tool_command(patches):
    """Test command with parametrized arguments."""
    ctx = MagicMock()
    path = MagicMock()
    args = [MagicMock(), MagicMock()]
    tool = CLITool(ctx, path, MagicMock())
    patched = patches(
        ("CLITool.args",
         dict(new_callable=PropertyMock)),
        ("CLITool.tool_path",
         dict(new_callable=PropertyMock)),
        prefix="synca.mcp.common.tool.cli")

    with patched as (m_args, m_tool_path, ):
        m_args.return_value = args
        assert (
            tool.command
            == (m_tool_path.return_value, *args))

    assert "command" not in tool.__dict__


@pytest.mark.asyncio
async def test_cli_tool_execute(patches):
    """Test execute method."""
    cmd = (MagicMock(), MagicMock(), MagicMock())
    ctx = MagicMock()
    path = MagicMock()
    args = MagicMock()
    tool = CLITool(ctx, path, args)
    stdout = MagicMock()
    stderr = MagicMock()
    patched = patches(
        "asyncio",
        "str",
        ("CLITool.path",
         dict(new_callable=PropertyMock)),
        prefix="synca.mcp.common.tool.cli")

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


@pytest.mark.asyncio
async def test_cli_tool_pipeline(patches):
    """Test pipeline method with various parameters."""
    ctx = MagicMock()
    path = MagicMock()
    args = MagicMock()
    tool = CLITool(ctx, path, args)
    patched = patches(
        ("CLITool.command",
         dict(new_callable=PropertyMock)),
        "CLITool.execute",
        "CLITool.parse_output",
        "CLITool.response",
        prefix="synca.mcp.common.tool.cli")

    with patched as (m_command, m_exec, m_parse, m_format):
        m_exec.return_value = (MagicMock(), MagicMock(), MagicMock())
        m_parse.return_value = (
            MagicMock(), MagicMock(), MagicMock(), MagicMock())
        assert (
            await tool.pipeline()
            == m_format.return_value)

    assert (
        m_exec.call_args
        == [(m_command.return_value, ), {}])
    assert (
        m_parse.call_args
        == [m_exec.return_value, {}])
    assert (
        m_format.call_args
        == [m_parse.return_value, {}])


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
        prefix="synca.mcp.common.tool.cli")
    ctx = MagicMock()
    path = MagicMock()
    args = MagicMock()
    tool = CLITool(ctx, path, args)

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

    assert (
        m_path.call_args
        == [(path,), {}])
    assert (
        m_path.return_value.exists.call_args
        == [(), {}])
    if not exists:
        assert (
            e.value.args[0]
            == f"Path '{path}' does not exist")
        assert not m_path.return_value.is_dir.called
        return
    assert (
        m_path.return_value.is_dir.call_args
        == [(), {}])
    if not is_dir:
        assert (
            e.value.args[0]
            == f"Path '{path}' is not a directory")
