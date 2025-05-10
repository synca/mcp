from typing import Any


class GitHubError(Exception):
    pass


class GitHubToolError(Exception):
    pass


class GitHubRequestError(GitHubError):
    """Custom exception for GitHub API errors."""

    def __init__(
            self,
            message: str,
            status_code: int | None = None,
            response_data: Any = None) -> None:
        """Initialize with error details."""
        self.status_code = status_code
        self.response_data = response_data
        super().__init__(message)
