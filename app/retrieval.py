"""
STEP 2 of the pipeline: find the past proposal that's the closest structural
and tonal match to this new call, so the drafting agent has something real
to work from instead of writing from a blank page every time.

Uses a local sentence-transformers embedding model + FAISS. No vector DB
server to stand up, no extra API key, no Docker — everything runs
in-process and persists to two small files on disk. Good enough for
5-8 documents. If this were going to production with hundreds of past
proposals, this is the exact point where you'd swap in Qdrant (same
pattern used in the SCM Assistant build) for filtering, metadata search
and horizontal scale.
"""
import json
from pathlib import Path

import faiss
from sentence_transformers import SentenceTransformer

BASE_DIR = Path(__file__).parent.parent
PROPOSALS_DIR = BASE_DIR / "data" / "past_proposals"
INDEX_PATH = BASE_DIR / "data" / "proposal_index.faiss"
META_PATH = BASE_DIR / "data" / "proposal_meta.json"

_model = None


def get_model() -> SentenceTransformer:
    global _model
    if _model is None:
        _model = SentenceTransformer("all-MiniLM-L6-v2")
    return _model


def build_index() -> None:
    """Run this once (or whenever you add a new past proposal)."""
    model = get_model()
    texts, meta = [], []

    for f in sorted(PROPOSALS_DIR.glob("*.md")):
        content = f.read_text()
        texts.append(content)
        meta.append({"filename": f.name, "content": content})

    if not texts:
        raise RuntimeError(f"No .md files found in {PROPOSALS_DIR}")

    embeddings = model.encode(texts, convert_to_numpy=True, normalize_embeddings=True)
    index = faiss.IndexFlatIP(embeddings.shape[1])  # cosine sim via normalized dot product
    index.add(embeddings)

    faiss.write_index(index, str(INDEX_PATH))
    META_PATH.write_text(json.dumps(meta))
    print(f"Indexed {len(texts)} past proposals -> {INDEX_PATH}")


def retrieve_best_proposal(extraction: dict, k: int = 1) -> dict:
    if not INDEX_PATH.exists():
        raise RuntimeError("No index found. Run `python scripts/build_index.py` first.")

    model = get_model()
    index = faiss.read_index(str(INDEX_PATH))
    meta = json.loads(META_PATH.read_text())

    query = (
        f"Industry: {extraction['industry']}. "
        f"Requested: {', '.join(extraction['deliverables_requested'])}. "
        f"Pain points: {', '.join(extraction['pain_points'])}."
    )
    query_vec = model.encode([query], convert_to_numpy=True, normalize_embeddings=True)
    scores, idxs = index.search(query_vec, k)

    best = dict(meta[idxs[0][0]])
    best["match_score"] = float(scores[0][0])
    return best
