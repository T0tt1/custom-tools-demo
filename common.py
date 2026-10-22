import anthropic

client = anthropic.Anthropic()

# Shared request settings. Low effort keeps the demo snappy on stage;
# fallbacks re-run the request on another model if a safety classifier declines.
REQUEST = dict(
    model="claude-opus-5-5",
    max_tokens=16000,
    output_config={"effort": "low"},
    betas=["server-side-fallback-2026-07-01"],
    fallbacks="default",
)

QUESTION = (
    "Hi, I'm anna@example.com. How many points do I have, and can I afford "
    "free shipping? If I can, please redeem it for me."
)


class C:
    BLUE, GREEN, YELLOW, MAGENTA, DIM, BOLD, END = (
        "\033[94m", "\033[92m", "\033[93m", "\033[95m", "\033[2m", "\033[1m", "\033[0m",
    )
