# How custom tools work: live demo

A loyalty shop assistant. Claude can only look up a customer, check points, list rewards and redeem one by calling **our** Python functions.

## Setup (do this before the session)

```bash
git clone https://github.com/T0tt1/custom-tools-demo && cd custom-tools-demo
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
export ANTHROPIC_API_KEY=sk-ant-...  # optional, see below
python step2_manual_loop.py        # dry run once, so you know the network and credentials work
```

**Credentials:** if `ANTHROPIC_API_KEY` is set, the demo uses the Claude API. If it isn't, it uses Amazon Bedrock with your current AWS credentials (region `us-east-1`, or `AWS_REGION`). Your AWS role needs Bedrock access to `anthropic.claude-opus-5-5`.

Use a large terminal font, a dark theme, and have `shop.py` open in an editor next to the terminal.

## Files

| File | What it shows |
|---|---|
| `shop.py` | The "real world": a fake DB, plain Python functions, and the JSON tool definitions |
| `step1_no_tools.py` | The model alone: it can talk, but it cannot know or do anything |
| `step2_manual_loop.py` | The agent loop written by hand, with every round-trip printed |
| `step3_tool_runner.py` | The same agent, with the SDK generating the schema and running the loop |

## Run of show (~15 min)

### 1. Problem: the model is a brain without hands (2 min)
```bash
python step1_no_tools.py
```
Claude answers politely that it can't see Anna's account. **Say:** "The model knows a lot about the world, but it knows nothing about *our* systems and it can't change anything."

### 2. What a tool is (3 min)
Open `shop.py` and point at three things:
1. **The function** (`redeem_reward`): ordinary code. It runs on our machine, with our permissions.
2. **The definition** (`TOOLS`): a name, a description and a JSON Schema. **Say:** "This text is *all* the model sees. It never sees the code."
3. **The description is a prompt.** Point at the line *"This SPENDS their points -- only call it when the customer asked to redeem."*

### 3. The loop, slowed down (5 min): the core of the demo
```bash
python step2_manual_loop.py --show-request --step
```
Press Enter between round-trips and narrate:
- **Call #1**: we send the question plus the tool menu. Claude replies `stop_reason = tool_use` and asks for `find_customer(anna@...)`. **Say:** "Claude didn't run anything. It *asked* us to."
- We run the function and send back a `tool_result`, matched by `tool_use_id`.
- **Call #2**: Claude now has `C-001` and asks for `get_points_balance` and `list_rewards`, often both in the same turn (parallel tool calls). **Say:** "It chained the output of one tool into the input of the next. That's planning."
- **Call #3**: `redeem_reward(C-001, R-10)`. This is a tool with a side effect.
- **Last call**: `stop_reason = end_turn`, and Claude gives its final answer.

Then show the ~20 lines of the loop in `step2_manual_loop.py`. **Key message:** "An agent is a `while` loop. The model decides, your code acts, and the results go back in."

### 4. Shortcut in production (2 min)
```bash
python step3_tool_runner.py
```
It prints the schema generated from the type hints and docstring, then runs the same conversation with no hand-written loop. **Say:** "In real projects you write the functions and the SDK does the plumbing."

### 5. Optional live tweaks (3 min, pick one)
- **Errors are data**: change the email in `common.py` to `boris@example.com` (he has 80 points). Claude usually sees the balance and doesn't redeem. If it tries anyway, the function's own check sends back `is_error: true`, and Claude explains the problem instead of crashing.
- **Descriptions steer behaviour**: delete the "only call it when the customer asked" sentence and the last line of the question ("If I can, please redeem it"). Discuss why guarding inside the function matters more than wording.
- **Unknown data**: ask about `nobody@example.com`.

## Takeaways for the slide
1. A tool is **a name, a description and a schema**. The model only reads the description.
2. The model **requests** tool calls. **Your code executes** them, so you keep control of auth, validation and side effects.
3. An agent is a **loop**: call the model, run the tools it asks for, send the results back, and repeat until `end_turn`.
4. Put safety checks **in the tool's code**, not only in its description.

## Tech notes
- Model: `claude-opus-5-5` at `effort: low`, to keep the demo fast. Raise the effort for harder tasks.
- `fallbacks: "default"` (Claude API only): if a safety classifier declines a request, the API re-runs it on another model.
- Each run costs a few cents. The fake DB resets every time a script starts.
