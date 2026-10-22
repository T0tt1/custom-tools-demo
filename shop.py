"""A fake loyalty shop: the "real world" our agent will reach through custom tools.

Nothing here knows about Claude. These are plain Python functions plus a
JSON description of each one -- that description is ALL the model ever sees.
"""

import json

# --- Fake database ---------------------------------------------------------

CUSTOMERS = {
    "anna@example.com": {"id": "C-001", "name": "Anna", "tier": "Gold"},
    "boris@example.com": {"id": "C-002", "name": "Boris", "tier": "Silver"},
}
POINTS = {"C-001": 1250, "C-002": 80}
REWARDS = [
    {"id": "R-10", "name": "Free shipping", "cost": 500},
    {"id": "R-20", "name": "$10 off coupon", "cost": 1000},
    {"id": "R-30", "name": "Mystery gift box", "cost": 3000},
]

# --- The actual functions (our code, runs on OUR machine) -------------------


def find_customer(email: str) -> dict:
    customer = CUSTOMERS.get(email.lower())
    if not customer:
        raise ValueError(f"No customer with email {email}")
    return customer


def get_points_balance(customer_id: str) -> dict:
    return {"customer_id": customer_id, "points": POINTS[customer_id]}


def list_rewards() -> list:
    return REWARDS


def redeem_reward(customer_id: str, reward_id: str) -> dict:
    reward = next(r for r in REWARDS if r["id"] == reward_id)
    if POINTS[customer_id] < reward["cost"]:
        raise ValueError(f"Not enough points for {reward['name']}")
    POINTS[customer_id] -= reward["cost"]
    return {"redeemed": reward["name"], "points_left": POINTS[customer_id]}


FUNCTIONS = {
    "find_customer": find_customer,
    "get_points_balance": get_points_balance,
    "list_rewards": list_rewards,
    "redeem_reward": redeem_reward,
}

# --- The tool definitions (what we SEND to Claude) --------------------------
# name + description + JSON Schema. The model picks tools by reading these.

TOOLS = [
    {
        "name": "find_customer",
        "description": "Look up a loyalty customer by email. Returns their customer id, name and tier.",
        "input_schema": {
            "type": "object",
            "properties": {"email": {"type": "string", "description": "Customer email address"}},
            "required": ["email"],
        },
    },
    {
        "name": "get_points_balance",
        "description": "Get the current loyalty points balance for a customer id (e.g. C-001).",
        "input_schema": {
            "type": "object",
            "properties": {"customer_id": {"type": "string"}},
            "required": ["customer_id"],
        },
    },
    {
        "name": "list_rewards",
        "description": "List all rewards in the catalog with their point cost.",
        "input_schema": {"type": "object", "properties": {}},
    },
    {
        "name": "redeem_reward",
        "description": "Redeem a reward for a customer. This SPENDS their points -- only call it when the customer asked to redeem.",
        "input_schema": {
            "type": "object",
            "properties": {
                "customer_id": {"type": "string"},
                "reward_id": {"type": "string", "description": "Reward id, e.g. R-10"},
            },
            "required": ["customer_id", "reward_id"],
        },
    },
]


def run_tool(name: str, tool_input: dict) -> tuple[str, bool]:
    """Execute a tool call. Returns (result_text, is_error)."""
    try:
        return json.dumps(FUNCTIONS[name](**tool_input)), False
    except Exception as e:
        return str(e), True
