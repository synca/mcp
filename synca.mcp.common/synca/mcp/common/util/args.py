"""Argument parsing utilities for Synca MCP."""

from typing import Any, cast

from synca.mcp.common import errors, types


class ArgParser:
    """Dictionary-based argument parser for Synca MCP tools."""

    def __init__(self) -> None:
        """Initialize the argument parser."""
        self.arguments: dict[str, types.ArgConfig] = {}

    def add_argument(self, name: str, **kwargs: Any) -> None:
        """Add an argument to the parser.
        """
        self.arguments[name] = cast(types.ArgConfig, kwargs)

    def parse_dict(self, args_dict: types.ArgsDict) -> types.ArgsDict:
        """Parse and validate a dictionary of arguments.
        """
        result: types.ArgsDict = {}
        for name, config in self.arguments.items():
            if value := self._handle_argument(args_dict, name, config):
                result[name] = value
        for name, value in args_dict.items():
            if name not in self.arguments and value is not None:
                result[name] = value
        return result

    def _handle_argument(
            self,
            args_dict: types.ArgsDict,
            name: str,
            config: types.ArgConfig) -> Any:
        if args_dict.get(name) is not None:
            return self._type_argument(args_dict[name], name, config)
        elif config.get("required", False):
            raise errors.ArgValueError(f"Required argument '{name}' is missing")
        elif "default" in config:
            return config["default"]
        return None

    def _type_argument(
            self,
            value: Any,
            name: str,
            config: types.ArgConfig) -> Any:
        if 'choices' in config and value not in config['choices']:
            raise errors.ArgValueError(
                f"Argument '{name}' must be one of {config['choices']}, "
                f"got '{value}'")
        if "type" in config and value is not None:
            try:
                return config["type"](value)
            except (ValueError, TypeError) as e:
                raise errors.ArgValueError(
                    f"Failed to convert '{name}' to "
                    f"{config['type'].__name__}: {e}")
        return value
