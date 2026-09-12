"""
Fast way to see and screenshot the core AI logic (extraction, retrieval,
drafting) without needing ngrok or the Telegram webhook wired up yet.

    python scripts/run_pipeline.py data/transcripts/call_1_marketing_agency.txt

This is Steps 1-3 of the write-up. Once this works cleanly on all three
sample transcripts, THEN move on to running the FastAPI server + Telegram
for the approval-loop part (Step 4).
"""
import json
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from app.extraction import extract_call_data
from app.retrieval import retrieve_best_proposal
from app.drafting import draft_proposal


def main(transcript_path: str) -> None:
    transcript = Path(transcript_path).read_text()

    print("=" * 70)
    print(f"STEP 1 — Loaded transcript: {transcript_path} ({len(transcript)} chars)")
    print("=" * 70)

    print("\nSTEP 2 — Extracting structured call data...\n")
    extraction = extract_call_data(transcript)
    print(json.dumps(extraction, indent=2))

    print("\n" + "=" * 70)
    print("STEP 3 — Retrieving closest past proposal...")
    print("=" * 70)
    matched = retrieve_best_proposal(extraction)
    print(f"\nMatched: {matched['filename']}  (similarity = {matched['match_score']:.3f})")

    print("\n" + "=" * 70)
    print("STEP 4 — Drafting the new proposal...")
    print("=" * 70 + "\n")
    draft = draft_proposal(extraction, matched)
    print(f"Subject: {draft['subject']}\n")
    print(draft["body"])


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python scripts/run_pipeline.py <path-to-transcript.txt>")
        sys.exit(1)
    main(sys.argv[1])
