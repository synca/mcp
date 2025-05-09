"""jq filter utility for processing JSON output."""

import jq  # type:ignore


class JQFilter:
    """Filter class for processing JSON with jq."""

    @classmethod
    def apply(
            cls,
            json_str: str,
            jq_filter: str | None) -> str:
        """Apply a jq filter to JSON data.

        Args:
            json_str: JSON string to filter
            jq_filter: jq filter to apply

        Returns:
            Filtered JSON string
        """
        if not jq_filter:
            return json_str
        return str(jq.compile(jq_filter).input_text(json_str).text())
