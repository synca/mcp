"""Base Tool class for MCP server tools."""

import traceback
from typing import Any


class Tool:
    """Base class for MCP server tools."""

    async def handle(self, *args: Any, **kwargs: Any) -> dict:
        """Handle the tool execution.

        This method should be implemented by subclasses.

        Returns:
            dict: Result of the tool execution
        """
        raise NotImplementedError("Subclasses must implement handle()")

    async def run(self, *args: Any, **kwargs: Any) -> dict:
        """Run the tool and handle exceptions.

        Returns:
            dict: Result of the tool execution or error information
        """
        try:
            return await self.handle(*args, **kwargs)
        except Exception as e:
            trace = traceback.format_exc()
            error_msg = f"Failed to run tool: {str(e)}\n{trace}"
            return {
                "success": False,
                "data": None,
                "error": error_msg
            }
