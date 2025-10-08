# MCP server for GDB/MI

An MCP server for interacting with GDB/MI (GDB Machine Interface).

Output from GDB/MI is "compressed" using `json5` to reduce the token count for
data structures. Hex values are also "compressed" by stripping out long
`0x00000000000` prefixes ie `0x0000004` becomes `0x4`

> [!CAUTION]
> GDB/MI can be very verbose, and this tool will destroy your
> quota VERY quickly if you are not careful with what you ask for! You have been
> warned.

## Installation

Clone the repo and install the deps:

```bash
pip install .
```

## Setup

### Claude CLI

```bash
# run the mcp server
fastmcp run gdb_mcp.py:mcp --transport http --port 3333

# add it to claude
claude mcp add --transport http gdb http://localhost:3333/mcp
```

### Gemini CLI (FastMCP and uv)

[Gemini CLI 🤝
FastMCP](https://developers.googleblog.com/en/gemini-cli-fastmcp-simplifying-mcp-server-development/)

This command simplifies the process and makes the server capabilities instantly
available and configured within Gemini CLI.

```bash
fastmcp install gemini-cli gdb_mcp.py
```

### Gemini CLI (Manual)

`.gemini/settings.json`

```json
{
  "mcpServers": {
    "GDB MCP Server": {
      "command": "fastmcp",
      "args": ["run", "/absolute/path/to/mcp-gdbmi/gdb_mcp.py:mcp"]
    }
  }
}
```

## Usage

Start your program with `gdbserver`:

```bash
gdbserver localhost:1234 ./program
```

Then use the tools through your MCP client:

Ask Claude/Gemini to:

- Set breakpoints
- Run the program
- Step through code
- Analyse registers
- Anything that is possible via the GDB machine interface

## Tools

### `connect(target: str)`

Connect to GDB, which connects to the target (e.g., `"localhost:1234"` for a gdbserver instance).

### `disconnect()`

Disconnect and terminate the GDB session.

### `command(command: str, wait_for_done: bool = True)`

Execute a GDB/MI command (e.g., `"-break-insert main"`, `"-exec-run"`).

## Common GDB/MI Commands

- `-break-insert LOCATION` - Set breakpoint
- `-break-delete NUM` - Delete breakpoint
- `-exec-run` - Start program
- `-exec-continue` - Continue execution
- `-exec-step` / `-exec-next` - Step through code
- `-stack-list-frames` - Show stack frames
- `-data-evaluate-expression EXPR` - Evaluate expression

See [GDB/MI docs](https://sourceware.org/gdb/onlinedocs/gdb/GDB_002fMI.html) for
more.

## License

[MIT](LICENSE.md)
