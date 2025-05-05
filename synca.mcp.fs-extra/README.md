# synca.mcp.fs-extra

[![codecov](https://codecov.io/gh/synca/mcp/branch/main/graph/badge.svg?flag=synca.mcp.fs-extra)](https://codecov.io/gh/synca/mcp)

Filesystem Extras MCP server

## Overview

This package provides an MCP server for filesystem-related tools:

- head
- tail
- grep
- sed

## Development

### Installation

```bash
$ git clone git@github.com:synca/mcp
$ cd mcp/synca.mcp.fs-extra
$ pip install -e .
```

### Claude Setup

Add the following to your `~/.config/Claude/claude_desktop_config.json`:

```json
"fs-extra": {
  "command": "uv",
  "args": [
      "run",
      "--with",
      "mcp[cli]",
      "--with-editable",
      "/path/to/mcp/synca.mcp.fs-extra",
      "python",
      "-m",
      "synca.mcp.fs_extra"
  ]
}
```
