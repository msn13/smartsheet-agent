from fastmcp import FastMCP
from tools import list_sheets as _list_sheets
from tools import generate_report as _generate_report

# The MCP server is ready for Claude Desktop. I ran the agent loop directly in terminal for the demo since
# it doesn't require any client setup.

mcp = FastMCP("smartsheet-agent")


@mcp.tool()
def list_sheets() -> str:
    """Lists all Smartsheets the user has access to with their names and IDs.
    Call this first when the user wants a report but hasn't specified which sheet."""
    return _list_sheets()


@mcp.tool()
def generate_report(sheet_id: str) -> str:
    """Generates an executive project status report for a specific Smartsheet.
    Use after list_sheets() to get the sheet ID. Returns a formatted Markdown report."""
    return _generate_report(sheet_id)


if __name__ == "__main__":
    mcp.run()  # starts the MCP server on stdio instead of https