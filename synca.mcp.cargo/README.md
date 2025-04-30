# synca.mcp.cargo

[![codecov](https://codecov.io/gh/synca/mcp/branch/main/graph/badge.svg?flag=synca.mcp.cargo)](https://codecov.io/gh/synca/mcp)

Cargo MCP server

## Overview

This package provides an MCP server for Rust development workflows using Cargo, including the following tools:

- **cargo_clippy**: Run the Clippy linter for Rust code
- **cargo_test**: Run tests for Rust projects
- **cargo_build**: Build Rust projects
- **cargo_check**: Check Rust code for errors without building
- **cargo_fmt**: Format Rust code using rustfmt
- **cargo_doc**: Generate documentation for Rust projects
- **cargo_run**: Run Rust project binaries
- **cargo_tarpaulin**: Run code coverage analysis for Rust projects

## Development

### Installation

```bash
$ git clone git@github.com:synca/mcp
$ cd mcp/synca.mcp.cargo
$ pip install -e .
```

### Claude Setup

Add the following to your `~/.config/Claude/claude_desktop_config.json`:

```json
"cargo": {
  "command": "uv",
  "args": [
      "run",
      "--with",
      "mcp[cli]",
      "--with-editable",
      "/path/to/mcp/synca.mcp.cargo",
      "python",
      "-m",
      "synca.mcp.cargo"
  ]
}
```
