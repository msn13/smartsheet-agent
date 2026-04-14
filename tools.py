import os, json, anthropic
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

ai_client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))


def _load_data() -> dict:
    # reads sample json
    with open("sample_data.json", "r") as f:
        return json.load(f)


def list_sheets() -> str:
    """Lists all available project sheets with their names and IDs.
    Call this first when the user asks about their sheets or wants a report
    but hasn't specified which sheet to use."""
    try:
        data = _load_data()
        sheets = [
            {"id": s["id"], "name": s["name"]}
            for s in data["sheets"]
        ]
        return json.dumps(sheets)
    except Exception as e:
        return json.dumps({"error": str(e)})


def fetch_sheet_data(sheet_id: str) -> str:
    """Fetches all task rows from a project sheet. Returns structured task data
    including status, owner, due date, and priority for each task."""
    try:
        data = _load_data()
        sheet = next((s for s in data["sheets"] if s["id"] == sheet_id), None)
        if not sheet:
            return json.dumps({"error": f"No sheet found with id {sheet_id}"})
        return json.dumps({"sheet_name": sheet["name"], "tasks": sheet["tasks"]})
    except Exception as e:
        return json.dumps({"error": str(e)})


def generate_report(sheet_id: str) -> str:
    """Generates an AI-written executive project status report for a Smartsheet.
    Use this when the user wants a report, summary, or status update on a project."""

    raw = json.loads(fetch_sheet_data(sheet_id))
    if "error" in raw:
        return f"Could not fetch sheet: {raw['error']}"

    sheet_name = raw["sheet_name"]
    tasks = raw["tasks"]

    # format tasks
    task_lines = "\n".join([
        f"- {t['task']} | Status: {t['status']} | Owner: {t['owner']} | Due: {t['due_date']} | Priority: {t['priority']}"
        for t in tasks
    ])

    prompt = f"""You are a project manager writing an executive status report for '{sheet_name}'.

Project tasks:
{task_lines}

Write a structured report with these exact sections:
## Executive Summary
A 2-3 sentence overview of overall project health.

## At-Risk Tasks
For each at-risk or overdue task: name the task, the owner, the due date, and a confidence rating (High/Medium/Low risk). Explain why it's at risk.

## Recommended Actions
Specific, actionable next steps. Name who should do what by when.

## Blockers
Anything preventing progress. If none, say "No blockers identified."

Keep the report under 400 words. Be direct and specific."""

    response = ai_client.messages.create(
        model="claude-haiku-4-5",
        max_tokens=512,
        messages=[{"role": "user", "content": prompt}]
    )
    report = response.content[0].text

    # save to file
    save_report(report, sheet_name)
    return report


def save_report(content: str, sheet_name: str) -> None:
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    filename = "report.md"
    header = f"# Status Report — {sheet_name}\n_Generated: {timestamp}_\n\n"
    with open(filename, "w") as f:
        f.write(header + content)


list_sheets()
fetch_sheet_data("1001")
generate_report("1001")