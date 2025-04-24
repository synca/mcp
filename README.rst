snake.mcp.server
================

.. image:: https://codecov.io/gh/yourusername/snake-mcp-server/branch/main/graph/badge.svg
  :target: https://codecov.io/gh/yourusername/snake-mcp-server

Python tools for the MCP server.

Tools
-----

- **pytest**: Run pytest on a Python project
- **flake8**: Run flake8 linter on a Python project

Installation
-----------

.. code-block:: bash

    pip install -e .

Usage
-----

Import and use the tools:

.. code-block:: python

    from snake.mcp.server.server import pytest, flake8

    # Run pytest
    result = await pytest(ctx, path="/path/to/python/project", verbose=True)

    # Run flake8
    result = await flake8(ctx, path="/path/to/python/project", max_line_length=88)
