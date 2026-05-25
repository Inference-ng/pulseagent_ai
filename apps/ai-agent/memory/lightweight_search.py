"""
Lightweight keyword-based search that replaces sentence-transformers at runtime.
No PyTorch, no neural model — just TF-IDF style matching using numpy only.
The FAISS index is still used for storage but we query it with pre-computed
average embeddings instead of a live model.
"""
import pickle
import os
import numpy as np
from typing import List, Dict, Any


class LightweightSearch:
    """
    Runtime search without sentence-transformers.
    Uses the pre-computed metadata directly with keyword matching.
    Falls back gracefully if FAISS index not found.
    """

    def __init__(self, metadata_path: str = None):
        base_dir = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "../../../data/processed")
        )
        self.metadata_path = metadata_path or os.path.join(base_dir, "items_metadata.pkl")
        self.metadata: Dict[int, dict] = {}
        self.load()

    def load(self):
        if os.path.exists(self.metadata_path):
            with open(self.metadata_path, "rb") as f:
                self.metadata = pickle.load(f)
            for v in self.metadata.values():
                if isinstance(v.get("category"), str):
                    v["category"] = v["category"].strip().title()

    def search(self, query: str, k: int = 10) -> List[Dict[str, Any]]:
        """
        Keyword search over product names and descriptions.
        Scores by number of query word matches.
        """
        if not self.metadata:
            return []

        query_words = set(query.lower().split())
        scored = []

        for idx, item in self.metadata.items():
            text = f"{item.get('name','')} {item.get('description','')} {item.get('category','')}".lower()
            score = sum(1 for word in query_words if word in text)
            # Boost by star rating if available
            stars = float(item.get('stars', 3.0) or 3.0)
            final_score = score + (stars / 10.0)
            scored.append((final_score, item))

        scored.sort(key=lambda x: x[0], reverse=True)
        return [item for _, item in scored[:k]]