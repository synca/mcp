
import pathlib

from synca.mcp.common.types import FileInfoDict


class FileInfo:

    def __init__(self, path: pathlib.Path) -> None:
        self.path = path

    @property
    def as_dict(self) -> FileInfoDict:
        return dict(
            path=str(self.path),
            size=self.path.stat().st_size,
            modified=self.path.stat().st_mtime)
