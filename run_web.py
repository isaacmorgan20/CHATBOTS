import os
import sys
from dotenv import load_dotenv

load_dotenv()

# Validate API key before launching
api_key = os.getenv("OPENROUTER_API_KEY", "")
if not api_key or api_key == "your-api-key-here":
    print("ERROR: OPENROUTER_API_KEY not set in .env file.")
    print("Edit the .env file and add your OpenRouter API key.")
    sys.exit(1)

import uvicorn

host = os.getenv("HOST", "127.0.0.1")
port = int(os.getenv("PORT", "8000"))

print(f"\n  NexSupport Web UI")
print(f"  Launching at -> http://{host}:{port}")
print(f"  Press Ctrl+C to stop.\n")

uvicorn.run("app:app", host=host, port=port, reload=False)
