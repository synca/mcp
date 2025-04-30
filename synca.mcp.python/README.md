# synca.mcp.python

[![codecov](https://codecov.io/gh/synca/mcp/branch/main/graph/badge.svg?flag=synca.mcp.python)](https://codecov.io/gh/synca/mcp)

Python MCP server

## Overview

This package provides an MCP server for Python development workflows, including the following tools:

- **pytest**: Run tests on Python projects with detailed reporting
- **mypy**: Perform type checking on Python code
- **flake8**: Lint Python code for style and potential errors

## Development

### Installation

```bash
$ git clone git@github.com:synca/mcp
$ cd mcp/synca.mcp.python
$ pip install -e .
```

### Claude Setup

Add the following to your `~/.config/Claude/claude_desktop_config.json`:

```json
"python": {
  "command": "uv",
  "args": [
      "run",
      "--with",
      "mcp[cli]",
      "--with-editable",
      "/path/to/mcp/synca.mcp.python",
      "python",
      "-m",
      "synca.mcp.python"
  ]
}
```
