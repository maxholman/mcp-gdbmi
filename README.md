# GDB MCP Server

An MCP server for interacting with GDB via gdbserver.

## Installation

Clone the repo and install the deps:

```bash
pip install .
```

## Setup

### Claude CLI

```bash
fastmcp run gdb_mcp.py:mcp --transport http --port 3333
claude mcp add --transport http gdb http://localhost:3333
```

### Gemini CLI

```bash
fastmcp install gemini-cli gdb_mcp.py
```

## Usage

Start your program with gdbserver:

```bash
gdbserver localhost:1234 ./program
```

Then use the tools through your MCP client:

```bash
# Ask Claude/Gemini to:
# - Set breakpoints
# - Run the program
# - Step through code
# - Analyse registers
```

## Tools

### `connect(target: str)`

Connect to a gdbserver instance (e.g., `"localhost:1234"`).

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

See [GDB/MI docs](https://sourceware.org/gdb/onlinedocs/gdb/GDB_002fMI.html) for more.

## License

[MIT](LICENSE.md)
