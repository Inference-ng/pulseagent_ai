import faiss
import pickle
import os
import logging

# ── Windows Terminal Fix + Offline Mode ───────────────────────────────────────
# sentence_transformers prints Unicode progress bars (████) during model load.
# On Windows with cp1252 terminals this causes a silent UnicodeEncodeError crash.
# These env vars must be set BEFORE importing sentence_transformers.
os.environ["HF_HUB_DISABLE_PROGRESS_BARS"] = "1"   # disables tqdm HF bars
os.environ["TRANSFORMERS_VERBOSITY"] = "error"       # silences transformers logs
os.environ["TOKENIZERS_PARALLELISM"] = "false"       # prevents tokenizer warnings
# ─────────────────────────────────────────────────────────────────────────────


logging.getLogger("sentence_transformers").setLevel(logging.ERROR)
logging.getLogger("huggingface_hub").setLevel(logging.ERROR)
logging.getLogger("transformers").setLevel(logging.ERROR)

# ── HuggingFace Auth Fix ──────────────────────────────────────────────────────
# sentence-transformers uses huggingface_hub internally. If any token is cached
# on this machine (even an expired one) it will try to authenticate and return
# a 401 Unauthorized error for public models.
# We patch get_token() to always return None, forcing anonymous (public) access.
import huggingface_hub
huggingface_hub.get_token = lambda *args, **kwargs: None

# Also clear any token env vars just in case
for _var in ("HF_TOKEN", "HUGGING_FACE_HUB_TOKEN", "HUGGINGFACE_HUB_TOKEN"):
    os.environ.pop(_var, None)
# ─────────────────────────────────────────────────────────────────────────────

from sentence_transformers import SentenceTransformer
from typing import List, Dict, Any


class FAISSStore:
    """
    FAISS-backed vector store for semantic product retrieval (Task B).
    Uses the all-MiniLM-L6-v2 sentence embedding model (384 dimensions).
    Loads a pre-built index from data/processed/ if available;
    otherwise initialises an empty index that can be populated with add_items().
    """

    def __init__(self, index_path: str = None, metadata_path: str = None):
        # Resolve data/processed/ relative to this file's location
        base_dir = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "../../../data/processed")
        )
        self.index_path = index_path or os.path.join(base_dir, "items.index")
        self.metadata_path = metadata_path or os.path.join(base_dir, "items_metadata.pkl")

        # Load the public embedding model (no auth needed)
        self.model = SentenceTransformer("paraphrase-MiniLM-L3-v2")
        self.index = None
        self.metadata: Dict[int, dict] = {}

        self.load()

    def load(self):
        """Load pre-built FAISS index and metadata from disk, or initialise empty."""
        if os.path.exists(self.index_path) and os.path.exists(self.metadata_path):
            self.index = faiss.read_index(self.index_path)
            with open(self.metadata_path, "rb") as f:
                self.metadata = pickle.load(f)
            # Normalise category capitalisation at load time so domain
            # filtering (lower-case comparison) works correctly.
            for v in self.metadata.values():
                if isinstance(v.get("category"), str):
                    v["category"] = v["category"].strip().title()
        else:
            # Empty flat L2 index (384 = all-MiniLM-L6-v2 embedding size)
            self.index = faiss.IndexFlatL2(384)
            self.metadata = {}

    def save(self):
        """Persist the FAISS index and metadata to disk."""
        os.makedirs(os.path.dirname(self.index_path), exist_ok=True)
        faiss.write_index(self.index, self.index_path)
        with open(self.metadata_path, "wb") as f:
            pickle.dump(self.metadata, f)

    def add_items(self, items: List[Dict[str, Any]]):
        """Embed and add a list of product dicts to the index, then save."""
        if not items:
            return
        texts = [
            f"{item.get('name', '')} {item.get('description', '')} {item.get('category', '')}"
            for item in items
        ]
        embeddings = self.model.encode(texts, convert_to_numpy=True)
        start_id = len(self.metadata)
        for i, item in enumerate(items):
            self.metadata[start_id + i] = item
        self.index.add(embeddings)
        self.save()

    def search(self, query: str, k: int = 10) -> List[Dict[str, Any]]:
        """
        Semantic search: returns the top-k most relevant items for a query.
        Returns an empty list if the index has no items yet.
        """
        if self.index is None or self.index.ntotal == 0:
            return []
        query_embedding = self.model.encode([query], convert_to_numpy=True)
        distances, indices = self.index.search(query_embedding, min(k, self.index.ntotal))
        results = []
        for i, idx in enumerate(indices[0]):
            if idx != -1 and idx in self.metadata:
                item = self.metadata[idx].copy()
                item["_distance"] = float(distances[0][i])
                results.append(item)
        return results
