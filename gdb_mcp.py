from fastmcp import FastMCP
from pygdbmi.gdbcontroller import GdbController
from typing import List, Dict, Optional, Any
import time
import json5
import re

# Initialize the MCP server
mcp = FastMCP("GDB MCP Server")

# Global variable to hold the GDB controller instance
gdbmi: Optional[GdbController] = None


def _process_hex_values(data: Any) -> Any:
    """
    Recursively traverses a data structure (dict, list) and shortens any
    hex address strings found (e.g., "0x00004000" becomes "0x4000").
    It uses a regex to ensure only valid, full-string hex values are processed.
    """
    if isinstance(data, dict):
        return {key: _process_hex_values(value) for key, value in data.items()}
    elif isinstance(data, list):
        return [_process_hex_values(item) for item in data]
    elif isinstance(data, str):
        # Use re.fullmatch to ensure the ENTIRE string is a valid hex number.
        # This is more accurate than startswith + try/except.
        # It handles the user's request for accuracy and 'word boundaries'
        # by matching the whole string from start (^) to end ($).
        if re.fullmatch(r"0x[0-9a-fA-F]+", data):
            # It's a valid hex string, so int() is safe.
            return hex(int(data, 16))
        # If it's not a hex string, return it unchanged.
        return data
    # For all other types, return the data unchanged.
    return data


def _serialize(data: Dict[str, Any]) -> str:
    """
    Central function to serialize a dictionary into a compact, relaxed,
    JavaScript-object-literal-style string.

    This first processes the data to shorten hex address strings, then uses
    the standard `json` library for robust, compact serialization, and finally
    uses a regex to safely unquote keys that are valid JavaScript identifiers.

    :param data: The Python dictionary to serialize.
    :return: A string formatted as a compact, single-line JS object literal.
    """
    # Step 1: Recursively process the data to shorten hex values.
    processed_data = _process_hex_values(data)

    # Step 2: Create a compact JSON string with no extra whitespace.
    compact_json = json5.dumps(
        processed_data,
        quote_keys=False,
        trailing_commas=False,
        quote_style=json5.QuoteStyle.PREFER_DOUBLE,
        indent=None,
        separators=(",", ":"),
    )

    return compact_json


def is_response_error(response: List[Dict]) -> Optional[str]:
    """
    Helper function to check if a GDB response contains an error.
    This is now safe against non-dict payloads.
    """
    for item in response:
        # GDB can return a mix of dicts and raw strings. Only process dicts.
        if isinstance(item, dict):
            payload = item.get("payload")
            is_error_message = item.get("message") == "error"

            # An error can be a top-level message OR a payload dict with a 'reason'.
            is_error_payload = isinstance(payload, dict) and payload.get("reason")

            if is_error_message or is_error_payload:
                error_msg = "Unknown GDB error."
                # Safely extract a more specific message from the payload.
                if isinstance(payload, dict):
                    error_msg = payload.get("msg", error_msg)
                # If payload exists but isn't a dict, it might be the message.
                elif payload is not None:
                    error_msg = str(payload)

                return f"GDB Error: {error_msg}"
    return None


@mcp.tool
def connect(target: str):
    """
    Connects the server's GDB instance to a remote gdbserver.

    This function is synchronous and waits for GDB's response to confirm
    the connection status.

    :param target: The target to connect to, e.g., 'localhost:1234'.
    :return: A serialized JSON5 string with the full response from GDB.
    """
    global gdbmi
    if gdbmi:
        gdbmi.exit()
        gdbmi = None

    try:
        gdbmi = GdbController()
        response = gdbmi.write(f"-target-select remote {target}", timeout_sec=5)

        error = is_response_error(response)
        if error:
            gdbmi.exit()
            gdbmi = None
            return _serialize({"status": "error", "message": error, "result": response})
        return _serialize({"result": response})
    except Exception as e:
        print(e)
        if gdbmi:
            gdbmi.exit()
            gdbmi = None
        return _serialize({"status": "error", "message": f"Spiver Error: {e}"})


@mcp.tool
def disconnect():
    """
    Disconnects and terminates the GDB session.
    :return: A serialized JSON5 string confirming the action.
    """
    global gdbmi
    if gdbmi:
        gdbmi.exit()
        gdbmi = None
        return _serialize(
            {"status": "ok", "message": "Disconnected and GDB process terminated."}
        )
    return _serialize({"status": "ok", "message": "No active session to disconnect."})


@mcp.tool
def command(command: str, wait_for_done: bool = True):
    """
    Executes a raw GDB MI command and waits for the result.

    :param command: The GDB MI command to execute, e.g., '-exec-run'.
    :param wait_for_done: If True, waits for a 'done' or 'running' status from GDB.
                          Set to False for commands that don't produce this, but it's
                          generally safer to leave it as True.
    :return: A serialized JSON5 string with the full response from GDB.
    """
    global gdbmi
    if not gdbmi:
        return _serialize(
            {"status": "error", "message": "Not connected to a GDB session."}
        )

    if wait_for_done:
        response = gdbmi.write(command, timeout_sec=10)
    else:
        gdbmi.write(command, timeout_sec=0)
        time.sleep(0.1)
        response = gdbmi.get_gdb_response(timeout_sec=5, raise_error_on_timeout=False)

    return _serialize({"result": response})


def main():
    """Entry point for the mcp-gdbmi command."""
    mcp.run()


if __name__ == "__main__":
    main()
