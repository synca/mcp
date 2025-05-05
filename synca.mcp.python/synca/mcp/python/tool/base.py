
from synca.mcp.common.types import OutputTuple
from synca.mcp.common.tool import CLICheckTool


class PythonTool(CLICheckTool):

    def parse_output(
            self,
            stdout: str,
            stderr: str,
            return_code: int) -> OutputTuple:
        """Parse the tool output.
        """
        if return_code > 1:
            raise RuntimeError(
                f"{self.tool_name} failed({return_code}): {stderr}")
        combined_output = stdout + "\n" + stderr
        issues_count = self.parse_issues(stdout, stderr)
        strip_out = combined_output.strip()
        message = (
            "No issues found"
            if issues_count == 0
            else f"Issues found: {issues_count}")
        return (
            return_code,
            message,
            (strip_out
             if strip_out
             else ""),
            {})

    def parse_issues(self, stdout: str, stderr: str) -> int:
        stdout_length = len(stdout.strip().splitlines())
        return (
            stdout_length
            if stdout.strip()
            else 0)
