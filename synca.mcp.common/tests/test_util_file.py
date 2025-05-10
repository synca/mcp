"""Isolated tests for synca.mcp.common.util.file."""

from unittest.mock import MagicMock

from synca.mcp.common.util.file import FileInfo


def test_file_info_constructor():
    """Test FileInfo class initialization."""
    path = MagicMock()
    file_info = FileInfo(path)
    assert file_info.path == path


def test_file_info_as_dict():
    """Test FileInfo as_dict property."""
    path = MagicMock()
    file_info = FileInfo(path)

    assert (
        file_info.as_dict
        == dict(
            path=str(path),
            size=path.stat.return_value.st_size,
            modified=path.stat.return_value.st_mtime))

    assert (
        path.stat.call_args_list
        == [[(), {}], [(), {}]])
    assert "as_dict" not in file_info.__dict__
