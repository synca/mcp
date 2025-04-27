# Context

This repository contains Python tools that use MCP (Model Context Protocol). These tools provide functionality for linting, testing, and type checking Python code, including tools like `flake8`, `pytest`, and `mypy`.

The MCP components in this repository are designed to integrate with these standard Python tools to enhance their functionality within the MCP ecosystem.

# Rules

* MUST NOT add trailing whitespace in any of these files
* MUST NOT write any scripts or other unwanted cruft unless specifically asked to
* SHOULD check the code base with the tools if they are available
* MUST end all files with a newline
* MUST NOT add unnecessary typing imports and should instead use modern typing hints
* SHOULD move any files to a directory called waste if you want to delete them
* MUST NOT add backwards compatibility unless explicitly told
* MUST NOT add workarounds/placeholders or other non-production code unless explicitly told
* SHOULD NOT use `Any` type annotations anywhere in the codebase

# Test Style Guide

* Method order in classes should follow this pattern:
  * Class methods (alphabetically ordered)
  * Slot methods (alphabetically ordered)
  * Public methods (alphabetically ordered)
  * Private methods (alphabetically ordered)

* Assertions in tests should follow these patterns:
  * For single line assertions, use `assert value == expected`
  * For multi-line assertions, use the following style:
    ```python
    assert (
        thing1
        == thing2)
    ```

* Mock call verification should use:
  ```python
  assert (
      mock.call_args
      == [(arg1, arg2), {"kwarg": value}])
  ```

* Test naming and organization:
  * Test file names should be in the format `test_{module_name}.py`
  * Test function names should be in the format `test_{class/function}_{feature}_{scenario}`
  * Use `@pytest.mark.parametrize` for comprehensive test coverage

* Reference implementations:
  * `test_server.py` - Reference for proper testing structure
  * `test_tools_base.py` - Reference for error handling tests
  * `test_tools_flake8.py` - Reference for mock verification and assertion styles
