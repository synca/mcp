
from mcp.server.fastmcp import Context

from synca.mcp.common.types import ResultDict
from synca.mcp.common.decorator import doc
from synca.mcp.gh_extra.tool.check import (
    CheckRunsTool, CheckSuitesTool, CheckRunsForSuiteTool)

from synca.mcp.gh_extra.server.base import DEBUGGING_WORKFLOW, mcp

RUNS_FOR_SUITE_DEBUGGING_FILTER = """
RECOMMENDED JQ FILTER FOR DEBUGGING CI:
jq=".check_runs
    | map(select(.conclusion == \"failure\")
          | .html_url
          | capture(".*runs/(?<run_id>[0-9]+)/.*")
          | .run_id)"
"""
RUNS_FOR_SUITE_ENDPOINT_INFO = """
This uses the endpoint to get check runs for a specific check suite:

    /get/repos/{owner}/{repo}/check-suites/{check_suite_id}/check-runs

The endpoint is documented here:

    https://docs.github.com/en/rest/checks/runs?apiVersion=2022-11-28#list-check-runs-in-a-check-suite
"""
SUITES_FOR_REF_ENDPOINT_INFO = """
This uses the endpoint to get check suite data:

    /get/repos/{owner}/{repo}/commits/{ref}/check-suites

The endpoint is documented here:

    https://docs.github.com/en/rest/checks/suites?apiVersion=2022-11-28#list-check-suites-for-a-git-reference
"""
SUITES_FOR_REF_DEBUGGING_FILTER = """
RECOMMENDED JQ FILTER FOR DEBUGGING CI:
jq=".check_suites
    | map(select(.conclusion == \"failure\"))
    | map(.id)"}
"""


@mcp.tool()
@doc(f"""
List check runs for a specific check suite.

TLDR: 👉 SECOND STEP after finding failing suites
      with `list_check_suites_for_ref`.

🔎 USE THIS AFTER finding failing suites with `list_check_suites_for_ref`.
This tool drills down into the specific failing runs within a suite.

{DEBUGGING_WORKFLOW}

{RUNS_FOR_SUITE_DEBUGGING_FILTER}

{RUNS_FOR_SUITE_ENDPOINT_INFO}

Args:
    ctx: The context object
    owner: Repository owner (username or organization)
    repo: Repository name
    check_suite_id: The ID of the check suite
    status: Optional filter by status
            (can be: "queued", "in_progress", "completed")
    check_name: Optional filter by check name
    filter: Optional filter type ("latest" or "all")
    per_page: Optional number of results per page (max 100)
    page: Optional page number for pagination
    jq: Optional jq filter to apply to the output

Returns:
    Dictionary containing check run information
""")
async def list_check_runs_for_check_suite(
        ctx: Context,
        owner: str,
        repo: str,
        check_suite_id: int,
        status: str | None = None,
        check_name: str | None = None,
        filter: str | None = None,
        per_page: int | None = None,
        page: int | None = 30,
        jq: str | None = None) -> ResultDict:
    return await CheckRunsForSuiteTool(
        ctx,
        dict(owner=owner,
             repo=repo,
             check_suite_id=check_suite_id,
             status=status,
             check_name=check_name,
             filter=filter,
             per_page=per_page,
             page=page,
             jq=jq)).run()


@mcp.tool()
@doc("""
List check runs for a Git reference.

TLDR: ❌ WRONG STARTING POINT for CI debugging.
      Use `list_check_suites_for_ref` instead.

CI DEBUGGING WORKFLOW:
1️⃣ FIRST: Use `list_check_suites_for_ref` to find failing suite IDs
2️⃣ THEN: Use `list_check_runs_for_check_suite` with those IDs
3️⃣ FINALLY: Use other tools only if needed with specific IDs

⚠STARTING HERE WILL FAIL: Results often include hundreds of check runs,
making it impossible to effectively identify failures.
Use `list_check_suites_for_ref` instead.

⚠ DON'T START HERE for finding failing CI.
Use `list_check_suites_for_ref` instead.

Check runs can be overwhelming with too many individual results, making
it hard to identify failures. Start with suites for a better overview.

This uses the endpoint to check CI status for a specific commit, branch,
or tag:

    /get/repos/{owner}/{repo}/commits/{ref}/check-runs

The endpoint is documented here:

    https://docs.github.com/en/rest/checks/runs?apiVersion=2022-11-28#list-check-runs-for-a-git-reference

Args:
    ctx: The context object
    owner: Repository owner (username or organization)
    repo: Repository name
    ref: The Git reference (can be a commit SHA, branch name, or tag name)
    check_name: Optional filter by check name
    status: Optional filter by status
           (can be: "queued", "in_progress", "completed")
    filter: Optional filter type ("latest" or "all")
    per_page: Optional number of results per page (max 100)
    page: Optional page number for pagination
    app_id: Optional filter by GitHub App ID
    jq: Optional jq filter to apply to the output

Returns:
    Dictionary containing check run information with status and conclusions

Examples:
    # Get the total number of check runs
    {"jq": ".total_count"}

    # Get only the check run names and statuses
    {"jq": ".check_runs
            | map({name: .name, status: .status,
                   conclusion: .conclusion})"}

    # Find failing check runs
    {"jq": ".check_runs
            | map(select(.conclusion == \"failure\"))
            | map(.name)"}

    # Get the latest completion time
    {"jq": ".check_runs | map(.completed_at) | max"}
""")
async def list_check_runs_for_ref(
        ctx: Context,
        owner: str,
        repo: str,
        ref: str,
        check_name: str | None = None,
        status: str | None = None,
        filter: str | None = None,
        per_page: int | None = None,
        page: int | None = None,
        app_id: int | None = None,
        jq: str | None = None) -> ResultDict:
    return await CheckRunsTool(
        ctx,
        dict(owner=owner,
             repo=repo,
             ref=ref,
             check_name=check_name,
             status=status,
             filter=filter,
             per_page=per_page,
             page=page,
             app_id=app_id,
             jq=jq)).run()


@mcp.tool()
@doc(f"""
List check suites for a specific commit.

TLDR: ✅ CORRECT STARTING POINT for finding failing CI.

👉 START HERE when trying to find failing CI for a branch or commit.
Check suites provide the most reliable and high-level view of CI status.
Other tools should be used only after you've identified failing suites.

RECOMMENDED FILTER FOR CI DEBUGGING:

{DEBUGGING_WORKFLOW}

{SUITES_FOR_REF_DEBUGGING_FILTER}

{SUITES_FOR_REF_ENDPOINT_INFO}

Check suites aggregate related check runs and provide a higher-level view.

Args:
    ctx: The context object
    owner: Repository owner (username or organization)
    repo: Repository name
    ref: The Git reference to get check suites for
         (commit SHA, branch name, or tag name)
    app_id: Optional filter by GitHub App ID
    check_name: Optional filter by check name
    per_page: Optional number of results per page (max 100)
    page: Optional page number for pagination
    jq: Optional jq filter to apply to the output

Returns:
    Dictionary containing check suite information
""")
async def list_check_suites_for_ref(
        ctx: Context,
        owner: str,
        repo: str,
        ref: str,
        app_id: int | None = None,
        check_name: str | None = None,
        per_page: int | None = 100,
        page: int | None = None,
        jq: str | None = None) -> ResultDict:
    return await CheckSuitesTool(
        ctx,
        dict(owner=owner,
             repo=repo,
             ref=ref,
             app_id=app_id,
             check_name=check_name,
             per_page=per_page,
             page=page,
             jq=jq)).run()
