import os

import anthropic

# Low effort keeps the demo snappy on stage.
REQUEST = dict(max_tokens=16000, output_config={"effort": "low"})

if os.environ.get("ANTHROPIC_API_KEY"):
    # Claude API: fallbacks re-run the request on another model if a safety classifier declines.
    client = anthropic.Anthropic()
    REQUEST |= dict(
        model="claude-opus-5-5",
        betas=["server-side-fallback-2026-07-01"],
        fallbacks="default",
    )
else:
    # No API key: use Amazon Bedrock with your current AWS credentials.
    client = anthropic.AnthropicBedrockMantle(aws_region=os.environ.get("AWS_REGION", "us-east-1"))
    REQUEST |= dict(model="anthropic.claude-opus-5-5")

QUESTION = (
    "Hi, I'm anna@example.com. How many points do I have, and can I afford "
    "free shipping? If I can, please redeem it for me."
)


class C:
    BLUE, GREEN, YELLOW, MAGENTA, DIM, BOLD, END = (
        "\033[94m", "\033[92m", "\033[93m", "\033[95m", "\033[2m", "\033[1m", "\033[0m",
    )
