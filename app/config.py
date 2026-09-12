"""
Central place every other module reads its secrets from.
Nothing here talks to the network — it just loads .env into memory.
"""
import os
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

MODEL_NAME = "openai/gpt-oss-120b"  # same model you already used in SCM Assistant

if not GROQ_API_KEY:
    raise RuntimeError(
        "GROQ_API_KEY is missing. Copy .env.example to .env and paste your key in "
        "(get one free at console.groq.com)."
    )
