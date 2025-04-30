"""Type definitions for the MCP common package."""

from typing import TypeAlias, TypedDict, NotRequired

IssuesTuple: TypeAlias = tuple[list[str], list[str], list[str]]


class StatusDict(TypedDict):
    status: str
    version: NotRequired[str | None]


class CoverageDict(TypedDict):
    total: float
    by_file: NotRequired[dict[str, float]]
    output_file: NotRequired[str | None]


class TimingInfoDict(TypedDict):
    total: str


class OutputInfoDict(TypedDict, total=False):
    # Common fields
    warnings_count: int
    errors_count: int
    warnings: list[str]
    errors: list[str]
    warning_messages: list[str]
    notes: list[str]
    resolutions: list[str]
    summary: NotRequired[dict[str, int | str] | None]
    mode: NotRequired[str | None]
    artifact_path: NotRequired[str | None]
    timing: NotRequired[TimingInfoDict | None]
    statuses: NotRequired[dict[str, StatusDict] | None]
    coverage: NotRequired[CoverageDict | None]

    compilation_output: NotRequired[str | None]
    program_output: NotRequired[str | None]

    # Specific to clippy tool
    warning_types: dict[str, int]
    error_types: dict[str, int]


OutputTuple: TypeAlias = tuple[int | None, int, str, OutputInfoDict]


class ResultDataDict(TypedDict):
    return_code: int
    message: str
    output: str
    project_path: str
    issues_count: int
    info: OutputInfoDict


class ResultDict(TypedDict):
    success: bool
    data: NotRequired[ResultDataDict | None]
    error: NotRequired[str | None]
