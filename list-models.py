import anthropic
import dotenv
dotenv.load_dotenv()
import os

client = anthropic.Anthropic(
    # defaults to os.environ.get("ANTHROPIC_API_KEY")
    api_key=os.getenv("ANTHROPIC_API_KEY"),
)

print("\n".join(list(map(lambda m: m.id, client.models.list().data))))
