"""
STEP 4 of the pipeline: push the draft to your phone as a Telegram message
with three inline buttons (Approve / Edit / Skip). This is the human-in-
the-loop gate — nothing gets sent to a real prospect without you tapping
Approve first.

Plain requests calls to the raw Telegram Bot HTTP API. No extra SDK, no
extra moving part to debug under time pressure.
"""
import requests

from app.config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID

API_URL = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}"


def send_approval_card(call_id: str, draft: dict) -> None:
    text = (
        f"\U0001F4C4 New proposal draft ready\n\n"
        f"*Subject:* {draft['subject']}\n\n"
        f"{draft['body'][:3500]}"
    )

    keyboard = {
        "inline_keyboard": [
            [
                {"text": "\u2705 Approve & Send", "callback_data": f"approve:{call_id}"},
                {"text": "\u270F\uFE0F Edit", "callback_data": f"edit:{call_id}"},
                {"text": "\u23ED Skip", "callback_data": f"skip:{call_id}"},
            ]
        ]
    }

    resp = requests.post(
        f"{API_URL}/sendMessage",
        json={
            "chat_id": TELEGRAM_CHAT_ID,
            "text": text,
            "parse_mode": "Markdown",
            "reply_markup": keyboard,
        },
        timeout=15,
    )
    resp.raise_for_status()


def answer_callback(callback_query_id: str, text: str) -> None:
    """A modal popup on the button-press, not a fast toast — show_alert=True
    means it stays on screen until you tap OK, which is what actually makes
    it screenshot-able instead of vanishing in ~2 seconds."""
    requests.post(
        f"{API_URL}/answerCallbackQuery",
        json={
            "callback_query_id": callback_query_id,
            "text": text,
            "show_alert": True,
        },
        timeout=15,
    )