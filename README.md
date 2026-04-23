# Smartsheet MCP Agent

An AI agent that connects to Smartsheets and autonomously generates structured project status reports using the Claude
API. Built with FastMCP and the Anthropic SDK.

## What It Does

Ask the agent in plain English — it figures out which Smartsheets to pull, reads the data, and writes an executive-ready
Markdown report. No manual data wrangling required.

```
uv run agent.py "List my sheets then generate a weekly status report for the first one"
```

```
Agent prompt: List my sheets then generate a weekly status report for the first one

  → list_sheets({})
  → generate_report({"sheet_id": "8432109876543", "report_type": "weekly"})
  → save_report({"content": "...", "filename": "report.md"})

Report saved to report.md
```

## Architecture

```
User prompt
    │
    ▼
Claude (claude-sonnet-4-6)
    │  decides which tools to call
    ▼
agent.py — tool loop
    ├── list_sheets()        → Smartsheet API
    ├── get_sheet_data()     → Smartsheet API
    ├── generate_report()    → Claude API (nested call)
    └── save_report()        → local .md file
```

**Tier 1** — `agent.py` calls `generate_report()` directly with a fixed sheet ID. One command, one report.  
**Tier 2** — `agent.py` runs the full agentic loop: Claude decides which tools to call and in what order.  
**Tier 3** — `mcp_server.py` exposes the same tools as a FastMCP server, usable by Claude Desktop or any MCP client.

## Setup

**Requirements:** Python 3.10+, a free [Smartsheet developer account](https://app.smartsheet.com),
an [Anthropic API key](https://console.anthropic.com).

```powershell
# 1. Install uv (Windows)
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"

# 2. Clone and enter the project
git clone https://github.com/yourusername/smartsheet-mcp-agent
cd smartsheet-mcp-agent

# 3. Install dependencies
uv sync

# 4. Set up your secrets
copy .env.example .env
# Edit .env and fill in your keys
```

**.env file:**

```
ANTHROPIC_API_KEY=sk-ant-...
SMARTSHEET_ACCESS_TOKEN=your-token-here
DEFAULT_SHEET_ID=your-sheet-id-here
```

## Usage

```powershell
# Run with the default prompt
uv run agent.py

# Run with a custom prompt
uv run agent.py "List all my sheets and give me an executive summary of each one"

# Start the MCP server (Tier 3 — connects to Claude Desktop)
uv run mcp_server.py
```

### Connecting to Claude Desktop (Tier 3)

Add this to `%AppData%\Claude\claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "smartsheet-agent": {
      "command": "uv",
      "args": [
        "--directory",
        "C:\\absolute\\path\\to\\smartsheet-mcp-agent",
        "run",
        "mcp_server.py"
      ]
    }
  }
}
```

Restart Claude Desktop — the Smartsheet tools will appear in the connector's menu.

## Example Output

```markdown
## Executive Summary
The Q3 Platform Migration project is 68% complete with 2 weeks remaining in the sprint.
Three tasks are actively blocked pending vendor access, putting the delivery date at medium risk.

## At-Risk Tasks
- **Backend API Migration** — Status: At Risk | Owner: Sarah K. | Due: Apr 18
  Confidence: High. Dependent on vendor credentials not yet provisioned.
- **Load Testing** — Status: Not Started | Owner: Dev Team | Due: Apr 20
  Confidence: Medium. Cannot begin until API migration completes.

## Recommended Actions
- Sarah K.: escalate vendor access ticket to IT by EOD Apr 15
- Dev Team: prepare load testing scripts in parallel so they are ready to run immediately

## Blockers
- Vendor portal access not provisioned (ticket #4821, opened Apr 10, no ETA)
```

## Project Structure

```
smartsheet-mcp-agent/
├── .env                  # secrets — never committed
├── .env.example          # template for new contributors
├── .gitignore
├── pyproject.toml        # dependencies managed by uv
├── agent.py              # Claude agent with agentic tool loop (Tier 2)
├── mcp_server.py         # FastMCP server (Tier 3)
└── README.md
```

## Extending This Project

**Add a new tool:** Define a function and add it to `TOOLS` in `agent.py`. For the MCP server, just decorate it with
`@mcp.tool()`.

**Schedule reports:** Wrap `run_agent()` in a cron job or Windows Task Scheduler to auto-generate daily reports.

**Multi-sheet summaries:** Prompt the agent to iterate over all sheets and produce a company-wide rollup.

**Email delivery:** Add a `send_email(report_content, recipient)` tool using `smtplib` or a transactional email API.

## Dependencies

| Package                 | Purpose                                        |
|-------------------------|------------------------------------------------|
| `anthropic`             | Claude API — chat completions and tool use     |
| `fastmcp`               | MCP server framework — `@mcp.tool()` decorator |
| `smartsheet-python-sdk` | Smartsheet API client                          |
| `python-dotenv`         | Load secrets from `.env` into environment      |

## License

MIT