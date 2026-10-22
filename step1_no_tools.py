"""Step 1 -- the model alone. No tools, so it can only talk; it cannot look anything up or act."""

from common import C, QUESTION, REQUEST, client

print(f"{C.BOLD}USER:{C.END} {QUESTION}\n")
response = client.beta.messages.create(**REQUEST, messages=[{"role": "user", "content": QUESTION}])
text = "".join(b.text for b in response.content if b.type == "text")
print(f"{C.GREEN}CLAUDE:{C.END} {text}")
