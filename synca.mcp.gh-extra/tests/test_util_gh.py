"""Isolated tests for synca.mcp.gh_extra.util.gh."""

from unittest.mock import AsyncMock, MagicMock, PropertyMock

import pytest
import aiohttp

from synca.mcp.gh_extra import errors
from synca.mcp.gh_extra.util import gh


def test_github_api_constructor():
    """Test the GitHubAPI constructor."""
    token = MagicMock()
    github_api = gh.GitHubAPI(token=token)
    assert github_api.token is token


@pytest.mark.asyncio
async def test_github_api_aenter():
    """Test the GitHubAPI __aenter__ method."""
    token = MagicMock()
    github_api = gh.GitHubAPI(token=token)
    assert (
        await github_api.__aenter__()
        == github_api)


@pytest.mark.parametrize("has_session", [True, False])
@pytest.mark.asyncio
async def test_github_api_aexit(has_session):
    """Test the GitHubAPI __aexit__ method."""
    token = MagicMock()
    github_api = gh.GitHubAPI(token=token)
    if has_session:
        session = AsyncMock()
        github_api.__dict__["session"] = session
    exc_type = MagicMock()
    exc_val = MagicMock()
    exc_tb = MagicMock()

    assert not await github_api.__aexit__(
        exc_type, exc_val, exc_tb)

    if has_session:
        assert (
            session.close.call_args
            == [(), {}])
    assert "session" not in github_api.__dict__


def test_github_api_api(patches):
    """Test the GitHubAPI api property."""
    token = MagicMock()
    github_api = gh.GitHubAPI(token)
    patched = patches(
        "_GitHubAPI",
        ("GitHubAPI.session",
         dict(new_callable=PropertyMock)),
        prefix="synca.mcp.gh_extra.util.gh")

    with patched as (m_ghapi, m_session):
        assert (
            github_api.api
            == m_ghapi.return_value)

    assert "api" in github_api.__dict__
    assert (
        m_ghapi.call_args
        == [(m_session.return_value, "synca-mcp-gh-extra"),
            {"oauth_token": token}])


@pytest.mark.parametrize(
    "has_write_path",
    [True, False])
def test_github_api_downloader(patches, has_write_path):
    """Test the GitHubAPI downloader property."""
    token = MagicMock()
    write_path = MagicMock() if has_write_path else None
    github_api = gh.GitHubAPI(token, write_path)
    patched = patches(
        "GitHubDownloader",
        ("GitHubAPI.session",
         dict(new_callable=PropertyMock)),
        prefix="synca.mcp.gh_extra.util.gh")

    with patched as (m_downloader, m_session):
        if not has_write_path:
            with pytest.raises(errors.GitHubToolError) as e:
                github_api.downloader
        else:
            assert (
                github_api.downloader
                == m_downloader.return_value)

    if not has_write_path:
        assert (
            str(e.value)
            == ("`write_path` must be set on "
                f"{github_api.__class__.__name__} to use download"))
        assert not m_downloader.called
        return

    assert "downloader" in github_api.__dict__
    assert (
        m_downloader.call_args
        == [(write_path, m_session.return_value, token), {}])


@pytest.mark.asyncio
async def test_github_api_download(patches):
    """Test the GitHubAPI download method."""
    token = MagicMock()
    write_path = MagicMock()
    github_api = gh.GitHubAPI(token, write_path)
    endpoint = MagicMock()
    params = MagicMock()
    expected_response = (MagicMock(), MagicMock(), MagicMock())
    patched = patches(
        ("GitHubAPI.downloader",
         dict(new_callable=PropertyMock)),
        "cast",
        prefix="synca.mcp.gh_extra.util.gh")

    with patched as (m_downloader, m_cast):
        m_downloader.return_value.download = AsyncMock(
            return_value=expected_response)
        assert (
            await github_api.download(endpoint, params)
            == expected_response)

    assert (
        m_cast.call_args
        == [(aiohttp.typedefs.Query, params), {}])
    assert (
        m_downloader.return_value.download.call_args
        == [(endpoint, m_cast.return_value), {}])


def test_github_api_session(patches):
    """Test the GitHubAPI session property."""
    github_api = gh.GitHubAPI(MagicMock())
    patched = patches(
        "aiohttp.ClientSession",
        prefix="synca.mcp.gh_extra.util.gh")

    with patched as (m_session, ):
        assert (
            github_api.session
            == m_session.return_value)

    assert "session" in github_api.__dict__
    assert (
        m_session.call_args
        == [(), {}])


@pytest.mark.asyncio
async def test_github_api_getitem(patches):
    """Test the GitHubAPI getitem method."""
    token = MagicMock()
    github_api = gh.GitHubAPI(token)
    endpoint = MagicMock()
    params = MagicMock()
    patched = patches(
        ("GitHubAPI.api",
         dict(new_callable=PropertyMock)),
        "json.dumps",
        prefix="synca.mcp.gh_extra.util.gh")

    with patched as (m_api, m_dumps):
        m_api.return_value.getitem = AsyncMock()
        assert (
            await github_api.getitem(endpoint, params)
            == (m_dumps.return_value, "Successfully retrieved item", 200))

    assert (
        m_api.return_value.getitem.call_args
        == [(endpoint,), {"url_vars": params}])
    assert (
        m_dumps.call_args
        == [(m_api.return_value.getitem.return_value,), {}])


@pytest.mark.asyncio
@pytest.mark.parametrize("per_page", [1, 3, 5, 10])
@pytest.mark.parametrize("pages", [None, 1, 2, 3])
async def test_github_api_getitems(patches, iters, per_page, pages):
    """Test the GitHubAPI getitems method."""
    token = MagicMock()
    github_api = gh.GitHubAPI(token)
    endpoint = MagicMock()
    params = MagicMock()
    iterable_key = MagicMock()
    items = iters()
    result_count = (pages or 1) * per_page
    total = min(result_count, 5)
    patched = patches(
        ("GitHubAPI.api",
         dict(new_callable=PropertyMock)),
        "json.dumps",
        "cast",
        prefix="synca.mcp.gh_extra.util.gh")

    with patched as (m_api, m_dumps, m_cast):
        m_api.return_value.getiter.return_value.__aiter__.return_value = items
        m_cast.return_value = per_page
        assert (
            await github_api.getitems(
                endpoint, params, pages, iterable_key)
            == (m_dumps.return_value,
                f"Successfully retrieved {total} items",
                200))

    assert (
        params.pop.call_args
        == [("per_page", 1), {}])
    assert (
        m_cast.call_args
        == [(int, params.pop.return_value), {}])
    assert (
        m_api.return_value.getiter.call_args
        == [(endpoint,),
            {"url_vars": params, "iterable_key": iterable_key}])
    assert (
        m_dumps.call_args
        == [({iterable_key: ["I0", "I1", "I2", "I3", "I4"][:result_count]},),
            {}])


# GitHubDownloader

def test_github_api_api_headers():
    """Test the GitHubAPI api_headers property."""
    write_path = MagicMock()
    session = MagicMock()
    token = MagicMock()
    downloader = gh.GitHubDownloader(write_path, session, token)

    assert (
        downloader.api_headers
        == {"Authorization": f"token {token}",
            "Accept": (
                "application/vnd.github.v3+json, "
                "application/vnd.github.VERSION.raw"),
            "User-Agent": "synca-mcp-gh-extra"})

    assert "api_headers" not in downloader.__dict__


def test_github_api_download_headers():
    """Test the GitHubAPI download_headers property."""
    write_path = MagicMock()
    session = MagicMock()
    token = MagicMock()
    downloader = gh.GitHubDownloader(write_path, session, token)

    assert (
        downloader.download_headers
        == {"Authorization": f"token {token}",
            "User-Agent": "synca-mcp-gh-extra"})

    assert "download_headers" not in downloader.__dict__


def test_github_downloader_download_info(patches):
    """Test the GitHubDownloader download_info method."""
    write_path = MagicMock()
    session = MagicMock()
    token = MagicMock()
    downloader = gh.GitHubDownloader(write_path, session, token)
    target_dir = MagicMock()
    patched = patches(
        "FileInfo",
        prefix="synca.mcp.gh_extra.util.gh")

    with patched as (m_file_info,):
        mock_files = [MagicMock() for _ in range(4)]
        for i, f in enumerate(mock_files):
            f.is_file.return_value = (i % 2 == 0)
        target_dir.rglob.return_value = mock_files
        assert (
            downloader.download_info(target_dir)
            == [m_file_info.return_value.as_dict
                for i, f in enumerate(mock_files)
                if i % 2 == 0])

    assert (
        target_dir.rglob.call_args
        == [("*",), {}])
    expected_file_info_calls = [
        [(f,), {}]
        for i, f in enumerate(mock_files)
        if i % 2 == 0]
    assert (
        m_file_info.call_args_list
        == expected_file_info_calls)


def test_github_downloader_extract(patches):
    """Test the GitHubDownloader extract method."""
    write_path = MagicMock()
    session = MagicMock()
    token = MagicMock()
    downloader = gh.GitHubDownloader(write_path, session, token)
    write_dir = MagicMock()
    zip_data = MagicMock()
    test_files = ["file1.txt", "file2.txt", "logs/file3.log"]
    patched = patches(
        "io.BytesIO",
        "zipfile.ZipFile",
        "FileInfo",
        prefix="synca.mcp.gh_extra.util.gh")

    with patched as (m_bytesio, m_zipfile, m_fileinfo):
        m_zip_instance = MagicMock()
        m_zipfile.return_value.__enter__.return_value = m_zip_instance
        m_zip_instance.namelist.return_value = test_files
        assert (
            downloader.extract(write_dir, zip_data)
            == [m_fileinfo.return_value.as_dict
                for _ in test_files])

    assert (
        m_bytesio.call_args
        == [(zip_data,), {}])
    assert (
        m_zipfile.call_args
        == [(m_bytesio.return_value.__enter__.return_value,), {}])
    assert (
        m_zip_instance.extractall.call_args
        == [(write_dir,), {}])
    assert (
        m_zip_instance.namelist.call_args
        == [(), {}])
    expected_fileinfo_calls = [
        [(write_dir / file,), {}]
        for file in test_files]
    assert (
        m_fileinfo.call_args_list
        == expected_fileinfo_calls)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "has_attachment",
    [True, False])
async def test_github_downloader_handle_attachment(patches, has_attachment):
    """Test the GitHubDownloader handle_attachment method."""
    write_path = MagicMock()
    session = MagicMock()
    token = MagicMock()
    downloader = gh.GitHubDownloader(write_path, session, token)
    target_dir = MagicMock()
    resp = MagicMock()
    resp.read = AsyncMock()
    content_disposition = (
        "attachment; filename=logs.zip"
        if has_attachment
        else "inline; filename=logs.zip")
    resp.headers.get.return_value = content_disposition
    patched = patches(
        "GitHubDownloader.extract",
        prefix="synca.mcp.gh_extra.util.gh")

    with patched as (m_extract,):
        if not has_attachment:
            with pytest.raises(gh.errors.GitHubRequestError) as e:
                await downloader.handle_attachment(target_dir, resp)
        else:
            assert (
                await downloader.handle_attachment(target_dir, resp)
                == m_extract.return_value)

    if not has_attachment:
        assert (
            "No 'attachment' found in Content-Disposition header"
            in str(e.value))
        assert (
            resp.headers.get.call_args
            == [("Content-Disposition", ""), {}])
        return
    assert (
        resp.headers.get.call_args
        == [("Content-Disposition", ""), {}])
    assert (
        resp.read.call_args
        == [(), {}])
    assert (
        m_extract.call_args
        == [(target_dir, resp.read.return_value), {}])


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "status_code",
    [200, 404])
async def test_github_downloader_handle_redirect(patches, status_code):
    """Test the GitHubDownloader handle_redirect method."""
    write_path = MagicMock()
    session = MagicMock()
    token = MagicMock()
    downloader = gh.GitHubDownloader(write_path, session, token)
    target_dir = MagicMock()
    download_url = MagicMock()
    patched = patches(
        ("GitHubDownloader.download_headers",
         dict(new_callable=PropertyMock)),
        "GitHubDownloader.extract",
        prefix="synca.mcp.gh_extra.util.gh")

    with patched as (m_download_headers, m_extract):
        resp = MagicMock()
        resp.status = status_code
        resp.read = AsyncMock()
        session.get.return_value.__aenter__.return_value = resp
        if status_code != 200:
            with pytest.raises(gh.errors.GitHubRequestError) as e:
                await downloader.handle_redirect(target_dir, download_url)
        else:
            assert (
                await downloader.handle_redirect(target_dir, download_url)
                == m_extract.return_value)

    assert (
        session.get.call_args
        == [(download_url,),
            {"headers": m_download_headers.return_value}])
    assert (
        session.get.return_value.__aenter__.call_args
        == [(), {}])
    if status_code != 200:
        assert f"Download failed with status {status_code}" in str(e.value)
        assert (
            getattr(e.value, "status_code", None)
            == status_code)
        return
    assert (
        resp.read.call_args
        == [(), {}])
    assert (
        m_extract.call_args
        == [(target_dir, resp.read.return_value), {}])


@pytest.mark.parametrize(
    "status",
    [200, 302, 404])
@pytest.mark.parametrize(
    "has_location",
    [True, False])
@pytest.mark.asyncio
async def test_github_downloader_handle_response(
        patches, status, has_location):
    """Test GitHub downloader's response handling method."""
    target_dir = MagicMock()
    url = MagicMock()
    download_url = MagicMock()
    resp = MagicMock()
    resp.status = status
    resp.headers.get.return_value = (
        download_url
        if has_location
        else None)
    downloader = gh.GitHubDownloader(
        MagicMock(),
        MagicMock(),
        "github_token")
    patched = patches(
        "GitHubDownloader.handle_attachment",
        "GitHubDownloader.handle_redirect",
        prefix="synca.mcp.gh_extra.util.gh")

    with patched as (m_handle_attachment, m_handle_redirect):
        if status == 200 or (status == 302 and has_location):
            assert (
                await downloader.handle_response(target_dir, url, resp)
                == (m_handle_redirect.return_value
                    if status == 302
                    else m_handle_attachment.return_value))
        else:
            with pytest.raises(errors.GitHubRequestError) as e:
                await downloader.handle_response(target_dir, url, resp)

    if status == 200:
        assert (
            m_handle_attachment.call_args
            == [(target_dir, resp), {}])
        assert not m_handle_redirect.called
        assert not resp.headers.get.called
        return
    elif status == 302:
        assert not m_handle_attachment.called
        assert (
            resp.headers.get.call_args
            == [("Location", ), {}])
        if has_location:
            assert (
                m_handle_redirect.call_args
                == [(target_dir, download_url), {}])
            return
    else:
        assert not m_handle_attachment.called
        assert not resp.headers.get.called
    assert not m_handle_redirect.called
    if status == 302:
        assert (
            str(e.value)
            == "Download URL not found in redirect")
        return
    assert (
        str(e.value)
        == f"Failed to download from {url}, got status {status}")
    assert (
        e.value.status_code
        == status)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "target_exists",
    [True, False])
async def test_github_downloader_download(patches, target_exists):
    """Test the GitHubDownloader download method."""
    write_path = MagicMock()
    session = MagicMock()
    token = MagicMock()
    downloader = gh.GitHubDownloader(write_path, session, token)
    endpoint = MagicMock()
    params = MagicMock()
    patched = patches(
        "json",
        ("GitHubDownloader.api_headers",
         dict(new_callable=PropertyMock)),
        "GitHubDownloader.download_info",
        "GitHubDownloader.handle_response",
        prefix="synca.mcp.gh_extra.util.gh")

    with patched as (m_json, m_api_headers, m_download_info,
                     m_handle_response):
        target_dir = write_path.__truediv__.return_value
        endpoint.strip.return_value.split.return_value = [
            "", "", "12345", "logs"]
        target_dir.exists.return_value = target_exists
        session.get.return_value.__aenter__.return_value = MagicMock()
        assert (
            await downloader.download(endpoint, params)
            == ((m_json.dumps.return_value,
                 (f"Logs ({len(m_download_info.return_value)}) "
                  f"for 12345 already downloaded"),
                 304)
                if target_exists
                else (m_json.dumps.return_value,
                      (f"Fetched logs ({len(m_handle_response.return_value)}) "
                       f"for 12345"),
                      200)))

    assert (
        endpoint.strip.call_args
        == [("/",), {}])
    assert (
        endpoint.strip.return_value.split.call_args
        == [("/",), {}])
    assert (
        write_path.__truediv__.call_args
        == [("12345",), {}])
    if target_exists:
        assert (
            m_download_info.call_args
            == [(target_dir,), {}])
        assert not session.get.called
        return
    assert (
        session.get.call_args
        == [(f"https://api.github.com{endpoint}",),
            {"headers": m_api_headers.return_value,
             "params": params}])
    assert (
        session.get.return_value.__aenter__.call_args
        == [(), {}])
    assert (
        m_handle_response.call_args
        == [(target_dir,
             f"https://api.github.com{endpoint}",
             session.get.return_value.__aenter__.return_value), {}])
