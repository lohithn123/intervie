#!/usr/bin/env python3
"""
Startup script for the AI Interviewer Platform.
Loads environment variables and starts the FastAPI server.
"""

import os
import sys
from dotenv import load_dotenv
import uvicorn

# Load environment variables
load_dotenv()

# Validate required environment variables
required_vars = ["OPENAI_API_KEY", "ELEVENLABS_API_KEY"]
missing_vars = [var for var in required_vars if not os.getenv(var) or os.getenv(var) == f"your-{var.lower().replace('_', '-')}-here"]

if missing_vars:
    print("⚠️  Missing or invalid environment variables:")
    for var in missing_vars:
        print(f"   - {var}")
    print("\nPlease update your .env file with valid API keys.")
    print("You can get these keys from:")
    print("   - OpenAI: https://platform.openai.com/api-keys")
    print("   - ElevenLabs: https://elevenlabs.io/api")
    sys.exit(1)

if __name__ == "__main__":
    print("🚀 Starting AI Interviewer Platform...")
    print(f"📍 Open http://localhost:8000 in your browser")
    print(f"📚 API docs available at http://localhost:8000/docs")
    print("\nPress CTRL+C to stop the server\n")
    
    # Run the FastAPI server
    uvicorn.run(
        "server:app",
        host="0.0.0.0",
        port=8000,
        reload=True,  # Enable auto-reload for development
        log_level="info"
    ) 