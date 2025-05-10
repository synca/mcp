"""Isolated tests for synca.mcp.gh_extra.tool.base."""

from unittest.mock import MagicMock, PropertyMock, AsyncMock

import pytest

from synca.mcp.gh_extra.tool import base


def test_github_tool_constructor():
    """Test the GitHubTool constructor."""
    ctx = MagicMock()
    args = MagicMock()
    tool = base.GitHubTool(ctx, args)
    assert tool.ctx == ctx
    assert tool._args == args
    assert tool.endpoint_tpl == ""
    assert tool.iterable_key is None
    assert tool._api_method is None
    assert tool.write_path is None
    assert "write_path" not in tool.__dict__


@pytest.mark.parametrize(
    "api_method",
    [None, "", "test_method"])
def test_github_tool_api_method(api_method):
    """Test the GitHubTool api_method property."""
    ctx = MagicMock()
    args = MagicMock()
    tool = base.GitHubTool(ctx, args)
    tool._api_method = api_method

    if api_method:
        assert tool.api_method == api_method
        assert "api_method" not in tool.__dict__
        return
    with pytest.raises(base.errors.GitHubToolError) as e:
        tool.api_method

    assert (
        e.value.args[0]
        == f"_api_method must be set for: {tool.__class__.__name__}")


def test_github_tool_arg_parser(patches):
    """Test the GitHubTool arg_parser property."""
    ctx = MagicMock()
    args = MagicMock()
    tool = base.GitHubTool(ctx, args)
    patched = patches(
        "ArgParser",
        "GitHubTool.add_arguments",
        prefix="synca.mcp.gh_extra.tool.base")

    with patched as (m_parser, m_add_arguments):
        assert (
            tool.arg_parser
            == m_parser.return_value)

    assert (
        m_parser.call_args
        == [(), {}])
    assert (
        m_add_arguments.call_args
        == [(m_parser.return_value,), {}])
    assert "arg_parser" not in tool.__dict__


def test_github_tool_args(patches):
    """Test the GitHubTool args cached property."""
    ctx = MagicMock()
    args = MagicMock()
    tool = base.GitHubTool(ctx, args)
    patched = patches(
        ("GitHubTool.arg_parser",
         dict(new_callable=PropertyMock)),
        prefix="synca.mcp.gh_extra.tool.base")

    with patched as (m_arg_parser,):
        assert (
            tool.args
            == m_arg_parser.return_value.parse_dict.return_value)

    assert (
        m_arg_parser.return_value.parse_dict.call_args
        == [(tool._args,), {}])
    assert "args" in tool.__dict__


def test_github_tool_add_arguments():
    """Test the GitHubTool add_arguments method."""
    ctx = MagicMock()
    args = MagicMock()
    tool = base.GitHubTool(ctx, args)
    parser = MagicMock()

    assert not tool.add_arguments(parser)

    assert (
        parser.add_argument.call_args
        == [("jq",),
            {"required": False,
             "help": "jq filter to apply to the output"}])


def test_github_tool_endpoint(patches, iters):
    """Test the GitHubTool endpoint property."""
    ctx = MagicMock()
    args = MagicMock()
    tool = base.GitHubTool(ctx, args)
    tool.endpoint_tpl = MagicMock()
    args_prop = iters(dict)
    patched = patches(
        ("GitHubTool.args",
         dict(new_callable=PropertyMock)),
        prefix="synca.mcp.gh_extra.tool.base")

    with patched as (m_args,):
        m_args.return_value = args_prop
        assert (
            tool.endpoint
            == tool.endpoint_tpl.format.return_value)

    assert (
        tool.endpoint_tpl.format.call_args
        == [(), args_prop])
    assert "endpoint" not in tool.__dict__


def test_github_tool_gh_api(patches):
    """Test the GitHubTool gh_api cached property."""
    ctx = MagicMock()
    args = MagicMock()
    tool = base.GitHubTool(ctx, args)
    patched = patches(
        "util.GitHubAPI",
        ("GitHubTool.gh_token",
         dict(new_callable=PropertyMock)),
        ("GitHubTool.write_path",
         dict(new_callable=PropertyMock)),
        prefix="synca.mcp.gh_extra.tool.base")

    with patched as (m_api, m_token, m_write):
        assert (
            tool.gh_api
            == m_api.return_value)

    assert (
        m_api.call_args
        == [(m_token.return_value,),
            dict(write_path=m_write.return_value)])
    assert "gh_api" in tool.__dict__


@pytest.mark.parametrize(
    "token",
    [None, "", "TEST_TOKEN"])
def test_github_tool_gh_token(patches, token):
    """Test the GitHubTool gh_token property."""
    ctx = MagicMock()
    args = MagicMock()
    tool = base.GitHubTool(ctx, args)
    patched = patches(
        "os",
        prefix="synca.mcp.gh_extra.tool.base")

    with patched as (m_os,):
        m_os.environ.get.return_value = token
        if token:
            assert tool.gh_token == token
        else:
            with pytest.raises(ValueError) as e:
                tool.gh_token

    assert (
        m_os.environ.get.call_args
        == [("GITHUB_TOKEN",), {}])
    assert "gh_token" not in tool.__dict__
    if not token:
        assert (
            str(e.value)
            == ("GITHUB_TOKEN environment variable is required "
                "for GitHub API access"))


def test_github_tool_request_data(patches):
    """Test the GitHubTool request_data property."""
    ctx = MagicMock()
    args = MagicMock()
    tool = base.GitHubTool(ctx, args)
    tool.iterable_key = MagicMock()
    patched = patches(
        ("GitHubTool.api_method",
         dict(new_callable=PropertyMock)),
        ("GitHubTool.endpoint",
         dict(new_callable=PropertyMock)),
        ("GitHubTool.args",
         dict(new_callable=PropertyMock)),
        prefix="synca.mcp.gh_extra.tool.base")

    with patched as (m_api_method, m_endpoint, m_args):
        assert (
            tool.request_data
            == dict(
                method=m_api_method.return_value,
                iterable_key=tool.iterable_key,
                pages=m_args.return_value.get.return_value,
                endpoint=m_endpoint.return_value,
                params=m_args.return_value))

    assert (
        m_args.return_value.get.call_args
        == [("pages", 1), {}])
    assert "request_data" not in tool.__dict__


def test_github_tool_parse_output(patches):
    """Test the GitHubTool parse_output method."""
    ctx = MagicMock()
    args = MagicMock()
    tool = base.GitHubTool(ctx, args)
    stdout = MagicMock()
    stderr = MagicMock()
    returncode = MagicMock()
    patched = patches(
        ("JQFilter.apply",
         dict(new_callable=MagicMock)),
        ("GitHubTool.args",
         dict(new_callable=PropertyMock)),
        prefix="synca.mcp.gh_extra.tool.base")

    with patched as (m_apply, m_args):
        assert (
            tool.parse_output(stdout, stderr, returncode)
            == (returncode,
                stderr,
                m_apply.return_value,
                {}))

    assert (
        m_apply.call_args
        == [(stdout, m_args.return_value.get.return_value), {}])
    assert (
        m_args.return_value.get.call_args
        == [("jq",), {}])


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "error",
    [None,
     BaseException,
     base.GitHubException,
     base.aiohttp.ClientError])
async def test_github_tool_request(patches, error):
    """Test the GitHubTool request method."""
    ctx = MagicMock()
    args = MagicMock()
    tool = base.GitHubTool(ctx, args)
    request = MagicMock()
    patched = patches(
        "GitHubTool._handle_request",
        ("GitHubTool.gh_api",
         dict(new_callable=PropertyMock)),
        prefix="synca.mcp.gh_extra.tool.base")

    with patched as (m_handle_request, m_api):
        if error:
            err = error("test error")
            if error == base.GitHubException:
                err.status_code = 500
                err.data = "response_data"
                m_handle_request.side_effect = err
            else:
                m_api.return_value.__aenter__.side_effect = err
            expected_error = (
                base.errors.GitHubRequestError
                if error in [base.GitHubException, base.aiohttp.ClientError]
                else error)
            with pytest.raises(expected_error) as e:
                await tool.request(request)
        else:
            assert (
                await tool.request(request)
                == m_handle_request.return_value)

    assert (
        m_api.return_value.__aenter__.call_args
        == [(), {}])
    if not error:
        assert (
            m_handle_request.call_args
            == [(m_api.return_value.__aenter__.return_value, request), {}])
    elif error == base.GitHubException:
        assert e.value.status_code == 500
        assert e.value.response_data == "response_data"
        assert f"GitHub API error: {err}" in str(e)
    elif error == base.aiohttp.ClientError:
        assert f"HTTP client error: {err}" in str(e)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "method",
    ["download", "getitem", "getitems", "invalid"])
async def test_github_tool_handle_request(patches, method):
    """Test the GitHubTool _handle_request method."""
    ctx = MagicMock()
    args = MagicMock()
    tool = base.GitHubTool(ctx, args)
    api = MagicMock()
    api.download = AsyncMock()
    api.getitem = AsyncMock()
    api.getitems = AsyncMock()
    request = MagicMock()

    def __getitem__(key):
        if key == "method":
            return method
        return MagicMock()

    request.__getitem__.side_effect = __getitem__

    if method == "invalid":
        with pytest.raises(base.errors.GitHubRequestError) as e:
            await tool._handle_request(api, request)
    else:
        assert (
            await tool._handle_request(api, request)
            == getattr(api, method).return_value)

    if method == "invalid":
        assert (
            request.__getitem__.call_args_list
            == [[("method",), {}], [("method",), {}]])
        assert (
            str(e.value)
            == f"Unsupported HTTP method: {method}")
        assert e.value.status_code == 400
        return
    assert (
        request.__getitem__.call_args_list
        == [(("method",), {}), (("endpoint",), {}), (("params",), {})])
    if method == "getitems":
        assert "iterable_key" in getattr(api, method).call_args[1]
        assert request.get.call_args == [("iterable_key",), {}]
    else:
        assert not getattr(api, method).call_args[1]
