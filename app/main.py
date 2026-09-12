"""
The "wiring" the assignment asks for. Two endpoints:

  POST /process-call     -> runs the full pipeline on a transcript,
                             sends the approval card to Telegram
  POST /telegram-webhook -> receives your button tap (Approve/Edit/Skip)
                             and finalizes the proposal

Run with: uvicorn app.main:app --reload --port 8000
Then expose it publicly with ngrok so Telegram can reach the webhook —
full steps are in README.md.
"""
import uuid
from pathlib import Path

from fastapi import FastAPI, Request

from app.graph import pipeline
from app.telegram_bot import answer_callback

app = FastAPI(title="Crework Proposal Agent")

STORE: dict[str, dict] = {}  # call_id -> {"draft":..., "status":...}
OUTPUT_DIR = Path(__file__).parent.parent / "output"
OUTPUT_DIR.mkdir(exist_ok=True)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/process-call")
def process_call(payload: dict):
    """
    Body: {"transcript": "<full call transcript text>"}
    """
    transcript = payload["transcript"]
    call_id = str(uuid.uuid4())[:8]

    result = pipeline.invoke({"call_id": call_id, "transcript": transcript})
    STORE[call_id] = {
        "extraction": result["extraction"],
        "matched_proposal": result["matched_proposal"]["filename"],
        "draft": result["draft"],
        "status": "awaiting_approval",
    }

    return {
        "call_id": call_id,
        "extraction": result["extraction"],
        "matched_proposal": result["matched_proposal"]["filename"],
        "match_score": result["matched_proposal"]["match_score"],
        "draft": result["draft"],
        "note": "Approval card sent to Telegram. Check your phone.",
    }


@app.post("/telegram-webhook")
async def telegram_webhook(request: Request):
    update = await request.json()
    cq = update.get("callback_query")
    if not cq:
        return {"ok": True}

    action, call_id = cq["data"].split(":")
    record = STORE.get(call_id)
    if not record:
        answer_callback(cq["id"], "This draft is no longer available.")
        return {"ok": True}

    if action == "approve":
        record["status"] = "sent"
        out_path = OUTPUT_DIR / f"proposal_{call_id}.md"
        out_path.write_text(
               f"# {record['draft']['subject']}\n\n{record['draft']['body']}",
               encoding="utf-8",
           )
        answer_callback(cq["id"], "Approved — saved to output/ (swap in your real send-email call here).")

    elif action == "skip":
        record["status"] = "skipped"
        answer_callback(cq["id"], "Skipped.")

    elif action == "edit":
        # Intentionally scoped out for this build: Approve and Skip are the
        # two fully-wired paths. Edit is flagged for manual follow-up rather
        # than looping back into a redraft — see WRITEUP.md Limitations.
        record["status"] = "needs_manual_edit"
        answer_callback(cq["id"], "Flagged for manual edit — not auto-redrafted in this version.")

    return {"ok": True}
