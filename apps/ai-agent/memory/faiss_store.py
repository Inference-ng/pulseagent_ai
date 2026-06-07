import pickle
import os
import logging
import numpy as np

logging.getLogger("sentence_transformers").setLevel(logging.ERROR)
logging.getLogger("huggingface_hub").setLevel(logging.ERROR)

from typing import List, Dict, Any


class FAISSStore:
    """
    Production-safe vector store.

    Priority:
      1. Neural search: FAISS IndexFlatIP + sentence-transformers (all-MiniLM-L6-v2)
         — used when the model is cached locally.
      2. TF-IDF + SVD search: FAISS IndexFlatIP + sklearn TfidfVectorizer/TruncatedSVD
         — used when sentence-transformers is unavailable (Render free tier, etc.)
      3. Keyword fallback: pure Python scoring, no FAISS required.
    """

    def __init__(self, index_path: str = None, metadata_path: str = None):
        # Skip neural mode in memory-constrained environments (Render free tier = 512MB)
        self._skip_neural = os.environ.get("DISABLE_NEURAL_SEARCH", "").lower() in ("1", "true", "yes")

        base_dir = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "../../../data/processed")
        )
        self.index_path    = index_path    or os.path.join(base_dir, "items.index")
        self.metadata_path = metadata_path or os.path.join(base_dir, "items_metadata.pkl")
        self.tfidf_path    = os.path.join(base_dir, "tfidf_model.pkl")

        self.metadata: Dict[int, dict] = {}
        self._mode      = "keyword"   # "neural" | "tfidf" | "keyword"
        self.model      = None        # sentence-transformers model (neural mode)
        self.index      = None        # faiss index
        self._tfidf_vec = None        # sklearn TfidfVectorizer (tfidf mode)
        self._tfidf_svd = None        # sklearn TruncatedSVD     (tfidf mode)

        self._load_metadata()
        if not self._skip_neural:
            self._try_load_neural()
        if self._mode == "keyword":
            self._try_load_tfidf()

    # ── loaders ──────────────────────────────────────────────────────────────

    def _load_metadata(self):
        if os.path.exists(self.metadata_path):
            with open(self.metadata_path, "rb") as f:
                self.metadata = pickle.load(f)
            for v in self.metadata.values():
                if isinstance(v.get("category"), str):
                    v["category"] = v["category"].strip().title()

    def _try_load_neural(self):
        try:
            import faiss
            from sentence_transformers import SentenceTransformer
            if os.path.exists(self.index_path):
                self.index = faiss.read_index(self.index_path)
                self.model = SentenceTransformer("all-MiniLM-L6-v2")
                self._mode = "neural"
        except Exception:
            pass

    def _try_load_tfidf(self):
        """Load the TF-IDF + SVD model that ships in the repo (data/processed/tfidf_model.pkl)."""
        try:
            import faiss
            if not os.path.exists(self.tfidf_path) or not os.path.exists(self.index_path):
                return
            with open(self.tfidf_path, "rb") as f:
                bundle = pickle.load(f)
            self._tfidf_vec = bundle["vectorizer"]
            self._tfidf_svd = bundle["svd"]
            self.index = faiss.read_index(self.index_path)
            self._mode = "tfidf"
        except Exception:
            pass

    # ── encoding ─────────────────────────────────────────────────────────────

    def _encode(self, text: str) -> np.ndarray:
        """Encode a query string into a 384-dim float32 vector."""
        if self._mode == "neural":
            vec = self.model.encode([text], convert_to_numpy=True).astype(np.float32)
        else:  # tfidf
            X = self._tfidf_vec.transform([text])
            vec = self._tfidf_svd.transform(X).astype(np.float32)
        # L2-normalise so IndexFlatIP == cosine similarity
        norm = np.linalg.norm(vec)
        if norm > 0:
            vec = vec / norm
        return vec

    # ── keyword fallback ─────────────────────────────────────────────────────

    def _keyword_search(self, query: str, k: int) -> List[Dict[str, Any]]:
        STOP = {'i','a','the','for','and','or','in','on','at','to','of',
                'is','it','me','my','want','need','looking','something','get','buy'}
        query_words = set(query.lower().split()) - STOP

        scored = []
        for item in self.metadata.values():
            text = f"{item.get('name','')} {item.get('description','')} {item.get('category','')}".lower()
            score = sum(1 for w in query_words if w in text)
            stars = float(item.get("stars", 3.0) or 3.0)
            scored.append((score + stars / 10.0, item))

        scored.sort(key=lambda x: x[0], reverse=True)
        top_score = scored[0][0] if scored else 0
        if top_score <= 0.3:
            return sorted(self.metadata.values(),
                          key=lambda x: float(x.get("stars", 0) or 0),
                          reverse=True)[:k]
        return [item for _, item in scored[:k]]

    # ── public API ───────────────────────────────────────────────────────────

    def search(self, query: str, k: int = 10) -> List[Dict[str, Any]]:
        if not self.metadata:
            return []

        if self._mode in ("neural", "tfidf") and self.index is not None:
            try:
                vec = self._encode(query)
                distances, indices = self.index.search(vec, min(k, self.index.ntotal))
                results = []
                for i, idx in enumerate(indices[0]):
                    if idx != -1 and idx in self.metadata:
                        item = self.metadata[idx].copy()
                        item["_score"] = float(distances[0][i])
                        results.append(item)
                return results
            except Exception:
                pass  # fall through to keyword

        return self._keyword_search(query, k)

    def add_items(self, items: List[Dict[str, Any]]):
        if not items or self._mode == "keyword":
            return
        texts = [f"{i.get('name','')} {i.get('description','')} {i.get('category','')}"
                 for i in items]
        start_id = len(self.metadata)
        for j, item in enumerate(items):
            self.metadata[start_id + j] = item
        embeddings = np.vstack([self._encode(t) for t in texts])
        self.index.add(embeddings)

    def save(self):
        if self._mode == "keyword":
            return
        import faiss
        os.makedirs(os.path.dirname(self.index_path), exist_ok=True)
        faiss.write_index(self.index, self.index_path)
        with open(self.metadata_path, "wb") as f:
            pickle.dump(self.metadata, f)
