"""
STEP 3 of the pipeline: structured call data + the closest past proposal
-> a new, tailored proposal draft.

The retrieved proposal is passed in as a STRUCTURAL/TONAL reference only.
The system prompt explicitly forbids copying its specific numbers, names
or scope — it's there to teach the model "this is roughly how we structure
an offer and how formal we sound," not to be quoted from.
"""
from groq import Groq

from app.config import GROQ_API_KEY, MODEL_NAME

client = Groq(api_key=GROQ_API_KEY)

DRAFTING_SYSTEM_PROMPT = """You are a senior proposal writer at an AI \
automation studio. You just got off a sales call and need to draft a \
proposal while the conversation is still fresh.

You will be given:
1. Structured data extracted from the call.
2. A past proposal, included ONLY as a structural and tonal reference.

Rules:
- Use the reference proposal to match section structure, formatting and \
tone (e.g. how formal, how much detail per section, how pricing is framed).
- NEVER copy the reference proposal's specific client name, numbers, \
pricing or scope into the new draft. Every fact must come from the call \
data provided.
- If budget or timeline was not discussed, do not invent numbers — leave \
a bracketed placeholder like [TBD on discovery call] instead.
- Keep it tight. A founder should be able to skim it in 90 seconds and \
send it with light editing, not a rewrite.

Output format (markdown):

Subject: <one line>

## Overview
## Scope of Work
## Deliverables
## Timeline
## Investment
## Next Steps
"""


def draft_proposal(extraction: dict, matched_proposal: dict) -> dict:
    user_prompt = f"""CALL DATA:
{extraction}

REFERENCE PROPOSAL (structure/tone only — do not copy its specifics):
{matched_proposal['content']}

Draft the new proposal now, addressed to {extraction['client_name']} at \
{extraction['company_name']}.
"""

    response = client.chat.completions.create(
        model=MODEL_NAME,
        temperature=0.4,  # a little room for natural phrasing, still controlled
        messages=[
            {"role": "system", "content": DRAFTING_SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
    )

    body = response.choices[0].message.content
    subject_line = f"Proposal for {extraction['company_name']}"

    return {"subject": subject_line, "body": body}
