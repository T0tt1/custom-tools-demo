"""Step 3 -- same agent, but the SDK writes the schema and runs the loop for us.

The schema comes from the type hints + docstring; the tool runner does the
call -> run tool -> send result -> call again cycle from step 2.
"""

import json

from anthropic import beta_tool

import shop
from common import C, QUESTION, REQUEST, client


@beta_tool
def find_customer(email: str) -> str:
    """Look up a loyalty customer by email. Returns their customer id, name and tier.

    Args:
        email: Customer email address.
    """
    return json.dumps(shop.find_customer(email))


@beta_tool
def get_points_balance(customer_id: str) -> str:
    """Get the current loyalty points balance for a customer id (e.g. C-001).

    Args:
        customer_id: The customer id.
    """
    return json.dumps(shop.get_points_balance(customer_id))


@beta_tool
def list_rewards() -> str:
    """List all rewards in the catalog with their point cost."""
    return json.dumps(shop.list_rewards())


@beta_tool
def redeem_reward(customer_id: str, reward_id: str) -> str:
    """Redeem a reward for a customer. This SPENDS their points -- only call it when the customer asked to redeem.

    Args:
        customer_id: The customer id.
        reward_id: Reward id, e.g. R-10.
    """
    return json.dumps(shop.redeem_reward(customer_id, reward_id))


tools = [find_customer, get_points_balance, list_rewards, redeem_reward]

print(f"{C.MAGENTA}Schema generated from the Python function:{C.END}")
print(json.dumps(redeem_reward.to_dict(), indent=2), "\n")

print(f"{C.BOLD}USER:{C.END} {QUESTION}\n")
runner = client.beta.messages.tool_runner(
    **REQUEST, tools=tools, messages=[{"role": "user", "content": QUESTION}]
)
for message in runner:
    for block in message.content:
        if block.type == "tool_use":
            print(f"{C.DIM}  tool call: {block.name}({json.dumps(block.input)}){C.END}")
        elif block.type == "text" and block.text.strip():
            print(f"{C.GREEN}CLAUDE:{C.END} {block.text}")
