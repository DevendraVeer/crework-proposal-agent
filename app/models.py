"""
Shape of the data as it moves through the graph.
Having this as real Pydantic models (not raw dicts) is what lets us
validate the LLM's JSON output instead of trusting it blindly.
"""
from pydantic import BaseModel
from typing import List


class CallExtraction(BaseModel):
    client_name: str
    company_name: str
    industry: str
    pain_points: List[str]
    deliverables_requested: List[str]
    budget_signal: str
    timeline: str
    decision_maker: bool
    next_steps: str
    urgency: str  # "low" | "medium" | "high"


class MatchedProposal(BaseModel):
    filename: str
    content: str
    match_score: float


class ProposalDraft(BaseModel):
    subject: str
    body: str
