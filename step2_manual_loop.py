"""Step 2 -- custom tools, with the agent loop written out by hand.

Run with --step to pause after every round-trip (good for presenting).
Run with --show-request to print the exact tool definitions sent to the API.
"""

import json
import sys

from common import C, QUESTION, REQUEST, client
from shop import TOOLS, run_tool

STEP = "--step" in sys.argv


def pause():
    if STEP:
        input(f"{C.DIM}  [enter to continue]{C.END}")


if "--show-request" in sys.argv:
    print(f"{C.MAGENTA}TOOLS SENT TO CLAUDE:{C.END}\n{json.dumps(TOOLS, indent=2)}\n")
    pause()

print(f"{C.BOLD}USER:{C.END} {QUESTION}\n")
messages = [{"role": "user", "content": QUESTION}]

for turn in range(1, 11):  # safety cap on loop iterations
    print(f"{C.DIM}── API call #{turn}: sending {len(messages)} messages + {len(TOOLS)} tool definitions ──{C.END}")
    response = client.beta.messages.create(**REQUEST, tools=TOOLS, messages=messages)
    print(f"{C.DIM}   stop_reason = {response.stop_reason}{C.END}")

    # Keep the whole assistant turn (text, tool_use, thinking blocks) in the history.
    messages.append({"role": "assistant", "content": response.content})

    for block in response.content:
        if block.type == "text" and block.text.strip():
            print(f"{C.GREEN}CLAUDE:{C.END} {block.text}")

    if response.stop_reason != "tool_use":
        break

    # Claude asked for tools. WE run them -- Claude never executes anything itself.
    tool_results = []
    for block in response.content:
        if block.type != "tool_use":
            continue
        print(f"{C.YELLOW}  → Claude wants: {block.name}({json.dumps(block.input)}){C.END}")
        result, is_error = run_tool(block.name, block.input)
        colour = C.MAGENTA if is_error else C.BLUE
        print(f"{colour}  ← we ran it, result: {result}{C.END}")
        tool_results.append(
            {"type": "tool_result", "tool_use_id": block.id, "content": result, "is_error": is_error}
        )

    # All results go back together, in ONE user message.
    messages.append({"role": "user", "content": tool_results})
    print()
    pause()
