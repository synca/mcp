from mcp.server.fastmcp import FastMCP


mcp = FastMCP(name="GitHub extra")

DEBUGGING_WORKFLOW = """
DEBUGGING WORKFLOW:
1. First use `list_check_suites_for_ref` to find failing check suite IDs
2. Use those suite IDs with this function to get specific failing
check runs
3. Focus on `head_sha` in the output to verify you're looking at the
right commit
"""


__all__ = (
    "DEBUGGING_WORKFLOW",
    "mcp")
