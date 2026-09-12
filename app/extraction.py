"""
STEP 1 of the pipeline: raw transcript -> structured JSON.

Why this exists: the drafting agent downstream should never see the raw
190-line transcript. It should see 8 clean fields. Separating "understand
the call" from "write the proposal" is the same lesson from the SCM
Assistant chunking work: don't make one prompt do two jobs.
"""
import json
from groq import Groq

from app.config import GROQ_API_KEY, MODEL_NAME
from app.models import CallExtraction

client = Groq(api_key=GROQ_API_KEY)

EXTRACTION_SYSTEM_PROMPT = """You are a sales operations analyst for an AI \
automation studio. You read raw sales call transcripts and pull out exactly \
the facts a proposal writer needs. You do not interpret, embellish or add \
anything the prospect did not say.

Return ONLY a valid JSON object with this exact shape, no markdown fences, \
no commentary before or after it:

{
  "client_name": "<first name of the prospect>",
  "company_name": "<their company>",
  "industry": "<one or two words>",
  "pain_points": ["<specific operational pain they described>", "..."],
  "deliverables_requested": ["<specific thing they asked to be built/fixed>", "..."],
  "budget_signal": "<any number, range, or budget language they used, or 'not discussed'>",
  "timeline": "<any deadline or urgency language they used, or 'not discussed'>",
  "decision_maker": true or false,
  "next_steps": "<what was agreed as the next action on the call>",
  "urgency": "low" | "medium" | "high"
}

If a field genuinely was not covered on the call, use "not discussed" rather \
than inventing something.
"""


def extract_call_data(transcript: str) -> dict:
    response = client.chat.completions.create(
        model=MODEL_NAME,
        temperature=0.1,  # low temp: this is extraction, not creative writing
        messages=[
            {"role": "system", "content": EXTRACTION_SYSTEM_PROMPT},
            {"role": "user", "content": f"CALL TRANSCRIPT:\n\n{transcript}"},
        ],
        response_format={"type": "json_object"},
    )
    raw = response.choices[0].message.content
    data = json.loads(raw)
    validated = CallExtraction(**data)  # raises if Groq's JSON doesn't match schema
    return validated.model_dump()
