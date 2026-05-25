import pickle
import os
import logging

logging.getLogger("sentence_transformers").setLevel(logging.ERROR)
logging.getLogger("huggingface_hub").setLevel(logging.ERROR)

from typing import List, Dict, Any


class FAISSStore:
    """
    Production-safe vector store.
    Uses LightweightSearch (no PyTorch) when sentence-transformers
    is not available — safe for Render 512MB free tier.
    Falls back to full neural search when running locally.
    """

    def __init__(self, index_path: str = None, metadata_path: str = None):
        base_dir = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "../../../data/processed")
        )
        self.index_path    = index_path    or os.path.join(base_dir, "items.index")
        self.metadata_path = metadata_path or os.path.join(base_dir, "items_metadata.pkl")
        self.metadata: Dict[int, dict] = {}
        self._use_neural = False
        self.model  = None
        self.index  = None

        self._load_metadata()
        self._try_load_neural()

    def _load_metadata(self):
        if os.path.exists(self.metadata_path):
            with open(self.metadata_path, "rb") as f:
                self.metadata = pickle.load(f)
            for v in self.metadata.values():
                if isinstance(v.get("category"), str):
                    v["category"] = v["category"].strip().title()

    def _try_load_neural(self):
        """Try to load FAISS + sentence-transformers. Silently skip if unavailable."""
        try:
            import faiss
            from sentence_transformers import SentenceTransformer
            if os.path.exists(self.index_path):
                self.index = faiss.read_index(self.index_path)
                self.model = SentenceTransformer("paraphrase-MiniLM-L3-v2")
                self._use_neural = True
        except Exception:
            self._use_neural = False

    def _keyword_search(self, query: str, k: int) -> List[Dict[str, Any]]:
        """Fast keyword search — no neural model needed."""
        query_words = set(query.lower().split())
        scored = []
        for item in self.metadata.values():
            text = f"{item.get('name','')} {item.get('description','')} {item.get('category','')}".lower()
            score = sum(1 for w in query_words if w in text)
            stars = float(item.get('stars', 3.0) or 3.0)
            scored.append((score + stars / 10.0, item))
        scored.sort(key=lambda x: x[0], reverse=True)
        return [item for _, item in scored[:k]]

    def search(self, query: str, k: int = 10) -> List[Dict[str, Any]]:
        if not self.metadata:
            return []
        if self._use_neural and self.index is not None:
            try:
                embedding = self.model.encode([query], convert_to_numpy=True)
                distances, indices = self.index.search(embedding, min(k, self.index.ntotal))
                results = []
                for i, idx in enumerate(indices[0]):
                    if idx != -1 and idx in self.metadata:
                        item = self.metadata[idx].copy()
                        item["_distance"] = float(distances[0][i])
                        results.append(item)
                return results
            except Exception:
                pass
        return self._keyword_search(query, k)

    def add_items(self, items: List[Dict[str, Any]]):
        if not items or not self._use_neural:
            return
        texts = [
            f"{item.get('name','')} {item.get('description','')} {item.get('category','')}}"
            for item in items
        ]
        embeddings = self.model.encode(texts, convert_to_numpy=True)
        start_id = len(self.metadata)
        for i, item in enumerate(items):
            self.metadata[start_id + i] = item
        self.index.add(embeddings)

    def save(self):
        if not self._use_neural:
            return
        import faiss
        os.makedirs(os.path.dirname(self.index_path), exist_ok=True)
        faiss.write_index(self.index, self.index_path)
        with open(self.metadata_path, "wb") as f:
            pickle.dump(self.metadata, f)