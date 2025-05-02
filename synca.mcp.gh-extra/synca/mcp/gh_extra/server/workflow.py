from mcp.server.fastmcp import Context

from synca.mcp.common.types import ResultDict
from synca.mcp.common.decorator import doc
from synca.mcp.gh_extra.tool.workflow import (
    WorkflowRunsTool, WorkflowLogsTool)

from synca.mcp.gh_extra.server.base import DEBUGGING_WORKFLOW, mcp


RUNS_ENDPOINT_INFO = """

This uses the endpoint to get workflow run data:

    /get/repos/{owner}/{repo}/actions/runs

The endpoint is documented here:

    https://docs.github.com/en/rest/actions/workflow-runs?apiVersion=2022-11-28#list-workflow-runs-for-a-repository
"""
WF_RUN_ENDPOINT_INFO = """

This uses the endpoint to get detailed workflow run information:

    /get/repos/{owner}/{repo}/actions/runs/{run_id}

The endpoint is documented here:

    https://docs.github.com/en/rest/actions/workflow-runs?apiVersion=2022-11-28#get-a-workflow-run

"""
WF_LOGS_ENDPOINT_INFO = """

This uses the endpoint to download workflow run logs:

    /get/repos/{owner}/{repo}/actions/runs/{run_id}/logs

The endpoint is documented here:

    https://docs.github.com/en/rest/actions/workflow-runs?apiVersion=2022-11-28#download-workflow-run-logs
"""


@mcp.tool()
@doc("""
List workflow runs for a repository.

TLDR: ❌ WRONG STARTING POINT for CI debugging.
      Use `list_check_suites_for_ref` instead.

⚠ STARTING HERE WILL FAIL: Results will be overwhelming and unreliable.
You will miss failing checks. Use `list_check_suites_for_ref` instead.

⚠ DON'T START HERE for finding failing CI.
   Use `list_check_suites_for_ref` instead.

Workflow runs often contain too much data and lack filtering by conclusion.

{DEBUGGING_WORKFLOW}

{RUNS_ENDPOINT_INFO}

Args:
    ctx: The context object
    owner: Repository owner (username or organization)
    repo: Repository name
    actor: Optional filter by username of the user who triggered
           the workflow
    branch: Optional filter by branch name
    event: Optional filter by event type (e.g. 'push', 'pull_request')
    status: Optional filter by status
            (can be: 'queued', 'in_progress', 'completed')
    per_page: Optional number of results per page (max 100)
    page: Optional page number for pagination
    created: Optional filter by workflow run creation time
             (ISO 8601 format)
    workflow_id: Optional workflow ID or filename to filter runs
    exclude_pull_requests: Optional whether to exclude pull request
                           workflow runs
    check_suite_id: Optional check suite ID to filter runs
    head_sha: Optional SHA to filter workflow runs
    jq: Optional jq filter to apply to the output

Returns:
    Dictionary containing workflow run information
""")
async def list_workflow_runs(
        ctx: Context,
        owner: str,
        repo: str,
        actor: str | None = None,
        branch: str | None = None,
        event: str | None = None,
        status: str | None = None,
        per_page: int | None = None,
        page: int | None = None,
        created: str | None = None,
        workflow_id: str | None = None,
        exclude_pull_requests: bool | None = None,
        check_suite_id: int | None = None,
        head_sha: str | None = None,
        jq: str | None = None) -> ResultDict:
    return await WorkflowRunsTool(
        ctx,
        dict(owner=owner,
             repo=repo,
             actor=actor,
             branch=branch,
             event=event,
             status=status,
             per_page=per_page,
             page=page,
             created=created,
             workflow_id=workflow_id,
             exclude_pull_requests=exclude_pull_requests,
             check_suite_id=check_suite_id,
             head_sha=head_sha,
             jq=jq)).run()


@mcp.tool()
@doc(f"""
Get details for a specific workflow run.

TLDR: ❌ WRONG STARTING POINT for CI debugging.
      Use `list_check_suites_for_ref` first.

⚠ DO NOT USE until you have a specific run ID from the proper workflow.
You cannot effectively find failing CI by starting here.

⚠ DON'T use this until you have a specific run ID from the proper
   debugging workflow.
Start with `list_check_suites_for_ref` to find failing CI first.

{DEBUGGING_WORKFLOW}

{WF_RUN_ENDPOINT_INFO}

Args:
    ctx: The context object
    owner: Repository owner (username or organization)
    repo: Repository name
    run_id: The workflow run ID
    exclude_pull_requests: Optional whether to exclude pull request
                           workflow runs

Returns:
    Dictionary containing detailed workflow run information
""")
async def get_workflow_run(
        ctx: Context,
        owner: str,
        repo: str,
        run_id: int,
        exclude_pull_requests: bool | None = None) -> ResultDict:
    return await WorkflowRunsTool(
        ctx,
        dict(owner=owner,
             repo=repo,
             run_id=run_id,
             exclude_pull_requests=exclude_pull_requests)).run()


@mcp.tool()
@doc(f"""
Get logs for a specific workflow run.

TLDR: ❌ WRONG STARTING POINT for CI debugging. Only use after the
         first two steps.

⚠ DO NOT USE until you have a specific run ID from the proper workflow.
Cannot be used effectively without first identifying the failing run.

⚠ DON'T use this until you have a specific run ID from thhe
   proper debugging workflow.
Use only after finding failing runs through check suites.

{DEBUGGING_WORKFLOW}

{WF_LOGS_ENDPOINT_INFO}

Args:
    ctx: The context object
    owner: Repository owner (username or organization)
    repo: Repository name
    run_id: The workflow run ID

Returns:
    Dictionary containing information about extracted log files and their
    locations

Examples:
    The tool extracts log files to
        /home/phlax/gitscratch/workflow-logs/{{owner}}/{{repo}}/{{run_id}}/
    and returns information about the extracted files including:
    - file_count: Number of log files extracted
    - files: List of file info dictionaries with path, size, etc.
""")
async def get_workflow_logs(
        ctx: Context,
        owner: str,
        repo: str,
        run_id: int) -> ResultDict:
    return await WorkflowLogsTool(
        ctx,
        dict(owner=owner,
             repo=repo,
             run_id=run_id)).run()
