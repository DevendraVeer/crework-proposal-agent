"""
Run once before anything else, and again any time you add/edit a file in
data/past_proposals/.

    python scripts/build_index.py
"""
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from app.retrieval import build_index

if __name__ == "__main__":
    build_index()
