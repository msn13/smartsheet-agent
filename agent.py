import os, anthropic, sys
from dotenv import load_dotenv
from tools import list_sheets, generate_report

load_dotenv()

ai = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

TOOLS = [
    {
        "name": "list_sheets",
        "description": "Lists all Smartsheets the user has access to. Call this first when the user wants a report but hasn't specified which sheet.",
        "input_schema": {"type": "object", "properties": {}, "required": []}
    },
    {
        "name": "generate_report",
        "description": "Generates an executive project status report for a specific Smartsheet. Use after list_sheets() to get the sheet ID.",
        "input_schema": {
            "type": "object",
            "properties": {
                "sheet_id": {
                    "type": "string",
                    "description": "The numeric Smartsheet ID from list_sheets()"
                }
            },
            "required": ["sheet_id"]
        }
    }
]

def execute_tool(name: str, inputs: dict) -> str:
    if name == "list_sheets":
        return list_sheets()
    elif name == "generate_report":
        return generate_report(inputs["sheet_id"])
    else:
        return f"Unknown tool: {name}"


def run_agent(user_prompt: str):
    print(f"\nAgent prompt: {user_prompt}\n")

    messages = [{"role": "user", "content": user_prompt}]

    while True:
        # send the full conversation so far + available tools to Claude
        response = ai.messages.create(
            model="claude-haiku-4-5",
            max_tokens=2048,
            tools=TOOLS,
            messages=messages
        )

        # add full response to the convo history
        messages.append({"role": "assistant", "content": response.content})

        if response.stop_reason == "end_turn":
            # Claude has a final text answer — print it and exit
            for block in response.content:
                if hasattr(block, "text"):
                    print("\nAgent complete:\n")
                    print(block.text)
            break

        # check if Claude wants to call tools —> find all tool_use blocks in the response
        tool_results = []
        for block in response.content:
            if block.type == "tool_use":
                print(f"  → {block.name}({block.input})")  # show progress
                result = execute_tool(block.name, block.input)
                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": block.id,  # must match the block.id sent
                    "content": result
                })

        # send all tool results back in one message
        messages.append({"role": "user", "content": tool_results})


if __name__ == "__main__":
    import sys

    prompt = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else \
        "List my Smartsheet's, then generate a status report for the first one."
    run_agent(prompt)