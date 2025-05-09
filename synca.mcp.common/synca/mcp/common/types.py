"""Type definitions for the MCP common package."""

from typing import Any, Callable, TypeAlias, TypedDict, NotRequired

from uritemplate import variable

ArgTuple: TypeAlias = tuple[str, ...]
CommandTuple: TypeAlias = tuple[str, ...]
ResponseTuple: TypeAlias = tuple[str, str, int]
IssuesTuple: TypeAlias = tuple[list[str], list[str], list[str]]


class CLIArgDict(TypedDict):
    args: NotRequired[ArgTuple | None]


class RequestDict(TypedDict):
    method: str
    endpoint: str
    headers: NotRequired[dict[str, str] | None]
    params: NotRequired[variable.VariableValueDict]
    payload: NotRequired[str | None]


class APIRequestDict(RequestDict):
    iterable_key: NotRequired[str | None]
    pages: NotRequired[int | None]


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

    project_path: NotRequired[str]
    issues_count: NotRequired[int]

    needs_formatting: NotRequired[bool]

    compilation_output: NotRequired[str | None]
    program_output: NotRequired[str | None]

    # Specific to clippy tool
    warning_types: dict[str, int]
    error_types: dict[str, int]

    # Specific to fs-extra tools (head, tail, etc.)
    lines_read: NotRequired[int]
    bytes_read: NotRequired[int]


OutputTuple: TypeAlias = tuple[int, str, str, OutputInfoDict]


class ResultDataDict(TypedDict):
    return_code: int
    message: str
    output: str
    info: OutputInfoDict


class ResultDict(TypedDict):
    data: NotRequired[ResultDataDict | None]
    error: NotRequired[str | None]


class ArgConfig(TypedDict):
    required: NotRequired[bool]
    default: NotRequired[Any]
    choices: NotRequired[list[Any]]
    type: NotRequired[Callable[[Any], Any]]
    help: NotRequired[str]


ArgsDict: TypeAlias = dict[str, Any]
