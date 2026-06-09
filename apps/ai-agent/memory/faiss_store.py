"""
apps/ai-agent/memory/faiss_store.py  —  PulseAgent AI (AWS Edition)
====================================================================
Vector store with three search tiers:

  1. Neural  — FAISS IndexFlatIP + sentence-transformers all-MiniLM-L6-v2
               (used when model is available and DISABLE_NEURAL_SEARCH != 1)
  2. TF-IDF  — FAISS IndexFlatIP + sklearn TfidfVectorizer/TruncatedSVD
               (fallback when sentence-transformers unavailable)
  3. Keyword — Pure Python scoring, no FAISS required.
               (last-resort fallback)

AWS integration:
  If the FAISS index files are absent locally but AWS_S3_BUCKET is set,
  FAISSStore automatically downloads them from S3 at startup.
  This keeps the Docker image lean — no 25 MB binary artifacts committed.

Environment variables:
  DISABLE_NEURAL_SEARCH=1      Force TF-IDF mode (saves ~1 GB RAM on small instances)
  AWS_S3_BUCKET=<bucket>       S3 bucket containing the FAISS artifacts
  AWS_S3_PREFIX=faiss/         S3 key prefix (default: "faiss/")
  AWS_DEFAULT_REGION=us-east-1 AWS region for S3 client
"""

import logging
import os
import pickle
from pathlib import Path
from typing import Any, Dict, List

import numpy as np

logging.getLogger("sentence_transformers").setLevel(logging.ERROR)
logging.getLogger("huggingface_hub").setLevel(logging.ERROR)

logger = logging.getLogger(__name__)


# ── S3 helper ─────────────────────────────────────────────────────────────────

def _download_from_s3(local_dir: Path) -> bool:
    """
    Download items.index, items_metadata.pkl, tfidf_model.pkl from S3.
    Returns True if all three files are present after the attempt.
    """
    bucket = os.environ.get("AWS_S3_BUCKET", "").strip()
    if not bucket:
        return False

    prefix = os.environ.get("AWS_S3_PREFIX", "faiss/").rstrip("/") + "/"
    targets = ["items.index", "items_metadata.pkl", "tfidf_model.pkl"]
    needed  = [t for t in targets if not (local_dir / t).exists()]

    if not needed:
        return True   # already cached locally

    try:
        import boto3
        s3 = boto3.client("s3")
        local_dir.mkdir(parents=True, exist_ok=True)
        for fname in needed:
            key   = f"{prefix}{fname}"
            local = local_dir / fname
            logger.info("[S3] Downloading s3://%s/%s → %s", bucket, key, local)
            s3.download_file(bucket, key, str(local))
            logger.info("[S3]   ✓ %s  (%d KB)", fname, local.stat().st_size // 1024)
        return True
    except Exception as e:
        logger.warning("[S3] Download failed: %s", e)
        return False


# ── FAISSStore ────────────────────────────────────────────────────────────────

class FAISSStore:
    """
    Production-safe vector store with automatic S3 artifact download.

    Priority:
      1. Neural search  — FAISS + sentence-transformers (all-MiniLM-L6-v2)
      2. TF-IDF search  — FAISS + sklearn TfidfVectorizer/TruncatedSVD
      3. Keyword search — pure Python scoring, no FAISS required
    """

    def __init__(self, index_path: str = None, metadata_path: str = None):
        self._skip_neural = os.environ.get("DISABLE_NEURAL_SEARCH", "").lower() in (
            "1", "true", "yes"
        )

        base_dir = Path(
            os.environ.get(
                "FAISS_DATA_DIR",
                str(Path(__file__).resolve().parents[3] / "data" / "processed"),
            )
        )

        self.index_path    = Path(index_path)    if index_path    else base_dir / "items.index"
        self.metadata_path = Path(metadata_path) if metadata_path else base_dir / "items_metadata.pkl"
        self.tfidf_path    = base_dir / "tfidf_model.pkl"

        self.metadata: Dict[int, dict] = {}
        self._mode      = "keyword"   # "neural" | "tfidf" | "keyword"
        self.model      = None        # SentenceTransformer (neural mode)
        self.index      = None        # faiss.Index
        self._tfidf_vec = None        # TfidfVectorizer (tfidf mode)
        self._tfidf_svd = None        # TruncatedSVD    (tfidf mode)

        # Try S3 download if any file is missing
        _download_from_s3(base_dir)

        self._load_metadata()
        if not self._skip_neural:
            self._try_load_neural()
        if self._mode == "keyword":
            self._try_load_tfidf()

        logger.info(
            "[FAISSStore] Loaded  items=%d  mode=%s  index_size=%s",
            len(self.metadata),
            self._mode,
            self.index.ntotal if self.index else "N/A",
        )

    # ── loaders ──────────────────────────────────────────────────────────────

    def _load_metadata(self):
        if self.metadata_path.exists():
            with open(self.metadata_path, "rb") as f:
                self.metadata = pickle.load(f)
            # Normalise category capitalisation
            for v in self.metadata.values():
                if isinstance(v.get("category"), str):
                    v["category"] = v["category"].strip().title()
        else:
            logger.warning("[FAISSStore] metadata file not found: %s", self.metadata_path)

    def _try_load_neural(self):
        try:
            import faiss
            from sentence_transformers import SentenceTransformer

            if not self.index_path.exists():
                logger.warning("[FAISSStore] FAISS index not found: %s", self.index_path)
                return

            logger.info("[FAISSStore] Loading neural FAISS index …")
            self.index = faiss.read_index(str(self.index_path))
            self.model = SentenceTransformer("all-MiniLM-L6-v2")
            self._mode = "neural"
            logger.info(
                "[FAISSStore] Neural mode active  (index=%d, model=all-MiniLM-L6-v2)",
                self.index.ntotal,
            )
        except ImportError:
            logger.info("[FAISSStore] sentence-transformers not installed — falling back to TF-IDF")
        except Exception as e:
            logger.warning("[FAISSStore] Neural load failed: %s", e)

    def _try_load_tfidf(self):
        """Load TF-IDF + SVD fallback that ships in data/processed/."""
        try:
            import faiss

            if not self.tfidf_path.exists() or not self.index_path.exists():
                logger.info("[FAISSStore] TF-IDF artifacts missing — using keyword search")
                return

            with open(self.tfidf_path, "rb") as f:
                bundle = pickle.load(f)
            self._tfidf_vec = bundle["vectorizer"]
            self._tfidf_svd = bundle["svd"]
            self.index      = faiss.read_index(str(self.index_path))
            self._mode      = "tfidf"
            logger.info("[FAISSStore] TF-IDF mode active  (index=%d)", self.index.ntotal)
        except Exception as e:
            logger.warning("[FAISSStore] TF-IDF load failed: %s", e)

    # ── encoding ─────────────────────────────────────────────────────────────

    def _encode(self, text: str) -> np.ndarray:
        """Encode a query string into a normalised float32 vector."""
        if self._mode == "neural":
            vec = self.model.encode([text], convert_to_numpy=True).astype(np.float32)
        else:
            X   = self._tfidf_vec.transform([text])
            vec = self._tfidf_svd.transform(X).astype(np.float32)

        norm = np.linalg.norm(vec)
        if norm > 0:
            vec = vec / norm
        return vec

    # ── keyword fallback ─────────────────────────────────────────────────────

    def _keyword_search(self, query: str, k: int) -> List[Dict[str, Any]]:
        STOP = {
            "i", "a", "the", "for", "and", "or", "in", "on", "at", "to", "of",
            "is", "it", "me", "my", "want", "need", "looking", "something",
            "get", "buy", "with", "some", "any", "best", "good",
        }
        query_words = set(query.lower().split()) - STOP

        scored: List[tuple] = []
        for item in self.metadata.values():
            text  = (
                f"{item.get('name','')} {item.get('description','')} "
                f"{item.get('category','')} {item.get('brand','')}"
            ).lower()
            score = sum(1 for w in query_words if w in text)
            stars = float(item.get("stars", 3.0) or 3.0)
            scored.append((score + stars / 10.0, item))

        scored.sort(key=lambda x: x[0], reverse=True)
        top_score = scored[0][0] if scored else 0
        if top_score <= 0.3:
            return sorted(
                self.metadata.values(),
                key=lambda x: float(x.get("stars", 0) or 0),
                reverse=True,
            )[:k]
        return [item for _, item in scored[:k]]

    # ── public API ───────────────────────────────────────────────────────────

    def search(self, query: str, k: int = 10) -> List[Dict[str, Any]]:
        if not self.metadata:
            return []

        if self._mode in ("neural", "tfidf") and self.index is not None:
            try:
                vec = self._encode(query)
                distances, indices = self.index.search(vec, min(k, self.index.ntotal))
                results: List[Dict[str, Any]] = []
                for i, idx in enumerate(indices[0]):
                    if idx != -1 and idx in self.metadata:
                        item          = self.metadata[idx].copy()
                        item["_score"] = float(distances[0][i])
                        results.append(item)
                return results
            except Exception as e:
                logger.warning("[FAISSStore] Vector search failed, falling back to keyword: %s", e)

        return self._keyword_search(query, k)

    def add_items(self, items: List[Dict[str, Any]]):
        """Add new items to the in-memory index (not persisted to disk)."""
        if not items or self._mode == "keyword":
            return

        texts = [
            f"{i.get('name','')} {i.get('description','')} "
            f"{i.get('category','')} {i.get('brand','')}"
            for i in items
        ]
        start_id = len(self.metadata)
        for j, item in enumerate(items):
            self.metadata[start_id + j] = item

        embeddings = np.vstack([self._encode(t) for t in texts])
        self.index.add(embeddings)

    def save(self):
        """Persist index and metadata to disk."""
        if self._mode == "keyword":
            return
        import faiss as _faiss
        self.index_path.parent.mkdir(parents=True, exist_ok=True)
        _faiss.write_index(self.index, str(self.index_path))
        with open(self.metadata_path, "wb") as f:
            pickle.dump(self.metadata, f)
        logger.info("[FAISSStore] Saved index (%d items) to %s", self.index.ntotal, self.index_path)

    @property
    def mode(self) -> str:
        return self._mode

    @property
    def total_items(self) -> int:
        return len(self.metadata)
