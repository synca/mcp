"""GitHub API utility module."""

import io
import json
import pathlib
import zipfile
from functools import cached_property
from typing import cast

import aiohttp
from gidgethub.aiohttp import GitHubAPI as _GitHubAPI
from uritemplate import variable

from synca.mcp.common.types import FileInfoDict, ResponseTuple
from synca.mcp.common.util import FileInfo
from synca.mcp.gh_extra import errors


class GitHubDownloader:

    def __init__(
            self,
            write_path: pathlib.Path,
            session: aiohttp.ClientSession,
            token: str) -> None:
        self.write_path = write_path
        self.session = session
        self.token = token

    @property
    def api_headers(self) -> dict[str, str]:
        return {
            "Authorization": f"token {self.token}",
            "Accept": (
                "application/vnd.github.v3+json, "
                "application/vnd.github.VERSION.raw"),
            "User-Agent": "synca-mcp-gh-extra"}

    @property
    def download_headers(self) -> dict[str, str]:
        return {
            "Authorization": f"token {self.token}",
            "User-Agent": "synca-mcp-gh-extra"}

    async def download(
            self,
            endpoint: str,
            params: aiohttp.typedefs.Query) -> ResponseTuple:
        run_id = endpoint.strip("/").split("/")[-2]
        target_dir = self.write_path / run_id
        if target_dir.exists():
            fileinfo = self.download_info(target_dir)
            return (
                json.dumps(fileinfo),
                f"Logs ({len(fileinfo)}) for {run_id} already downloaded",
                304)
        url = f"https://api.github.com{endpoint}"
        download = self.session.get(
            url,
            headers=self.api_headers,
            params=params)
        async with download as resp:
            fileinfo = await self.handle_response(target_dir, url, resp)
            return (
                json.dumps(fileinfo),
                f"Fetched logs ({len(fileinfo)}) for {run_id}",
                200)

    def download_info(self, target_dir: pathlib.Path) -> list[FileInfoDict]:
        return [
            FileInfo(file).as_dict
            for file in target_dir.rglob('*')
            if file.is_file()]

    def extract(
            self,
            write_dir: pathlib.Path,
            zip_data: bytes) -> list[FileInfoDict]:
        with io.BytesIO(zip_data) as zip_buffer:
            with zipfile.ZipFile(zip_buffer) as zip_file:
                all_files = zip_file.namelist()
                zip_file.extractall(write_dir)
                return [
                    FileInfo(write_dir / file).as_dict
                    for file
                    in all_files]

    async def handle_attachment(
            self,
            target_dir: pathlib.Path,
            resp) -> list[FileInfoDict]:
        if "attachment" not in resp.headers.get("Content-Disposition", ""):
            raise errors.GitHubRequestError(
                "No 'attachment' found in Content-Disposition header, "
                "unexpected response.")
        return self.extract(target_dir, await resp.read())

    async def handle_redirect(
            self,
            target_dir: pathlib.Path,
            download_url: str) -> list[FileInfoDict]:
        download = self.session.get(
            download_url,
            headers=self.download_headers)
        async with download as resp:
            if resp.status != 200:
                raise errors.GitHubRequestError(
                    f"Download failed with status {resp.status}",
                    status_code=resp.status)
            return self.extract(target_dir, await resp.read())

    async def handle_response(
            self,
            target_dir: pathlib.Path,
            url: str,
            resp) -> list[FileInfoDict]:
        match resp.status:
            case 200:
                return await self.handle_attachment(target_dir, resp)
            case 302:
                if download_url := resp.headers.get("Location"):
                    return await self.handle_redirect(target_dir, download_url)
                raise errors.GitHubRequestError(
                    "Download URL not found in redirect",
                    status_code=resp.status)
            case _:
                raise errors.GitHubRequestError(
                    f"Failed to download from {url}, got status {resp.status}",
                    status_code=resp.status)


class GitHubAPI:
    """Simplified GitHub API interface."""

    def __init__(
            self,
            token: str,
            write_path: pathlib.Path | None = None) -> None:
        self.token = token
        self.write_path = write_path

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if "session" in self.__dict__:
            await self.session.close()
            del self.__dict__["session"]

    @cached_property
    def api(self) -> _GitHubAPI:
        """Get authenticated GitHub API client."""
        return _GitHubAPI(
            self.session,
            "synca-mcp-gh-extra",
            oauth_token=self.token)

    @cached_property
    def downloader(self) -> GitHubDownloader:
        if not (write_path := self.write_path):
            raise errors.GitHubToolError(
                f"`write_path` must be set on {self.__class__.__name__} "
                "to use download")
        return GitHubDownloader(write_path, self.session, self.token)

    @cached_property
    def session(self) -> aiohttp.ClientSession:
        """Get authenticated GitHub API client."""
        return aiohttp.ClientSession()

    async def download(
            self,
            endpoint: str,
            params: variable.VariableValueDict) -> ResponseTuple:
        """Handle download requests."""
        return await self.downloader.download(
            endpoint,
            cast(aiohttp.typedefs.Query, params))

    async def getitem(
            self,
            endpoint: str,
            params: variable.VariableValueDict) -> ResponseTuple:
        """Handle GET requests."""
        return (
            json.dumps(await self.api.getitem(endpoint, url_vars=params)),
            "Successfully retrieved item",
            200)

    async def getitems(
            self,
            endpoint: str,
            params: variable.VariableValueDict,
            pages: int | None = 1,
            iterable_key: str | None = "items") -> ResponseTuple:
        """Handle iterating GET requests.
        """
        # TODO: add total available (ie pagination)
        results = []
        result_count = (pages or 1) * cast(int, params.pop("per_page", 1))
        iterable_key = iterable_key or "items"
        i = 0
        getitems = self.api.getiter(
            endpoint,
            url_vars=params,
            iterable_key=iterable_key)
        async for result in getitems:
            i += 1
            results.append(result)
            if i >= result_count:
                break
        return (
            json.dumps({iterable_key: results}),
            f"Successfully retrieved {i} items",
            200)
