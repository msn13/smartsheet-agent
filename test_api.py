import anthropic
from dotenv import load_dotenv

load_dotenv()  # load ANTHROPIC_API_KEY from .env into environment

client = anthropic.Anthropic()  # auto-read ANTHROPIC_API_KEY

message = client.messages.create(
    model="claude-haiku-4-5",
    max_tokens=256,
    messages=[
        {"role": "user", "content": "Say hello and confirm you are Claude."}
    ]
)

print(message.content[0].text)
print(f"\nTokens used — in: {message.usage.input_tokens}, out: {message.usage.output_tokens}")