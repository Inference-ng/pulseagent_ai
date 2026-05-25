"""
data/scripts/embed.py
Reads amazon_fashion.csv (from loader.py), embeds all items with
sentence-transformers, and writes the FAISS index + metadata to data/processed/.

Run from repo root:
    python data/scripts/embed.py
"""
import os
import logging
import pickle

import pandas as pd
import faiss

# ── HuggingFace Auth Fix ──────────────────────────────────────────────────────
# Force anonymous (public) model access — no HF token needed for all-MiniLM-L6-v2
# Force offline mode to use the locally cached model without any network calls.
os.environ["TRANSFORMERS_OFFLINE"] = "0"
os.environ["HF_DATASETS_OFFLINE"] = "0"
os.environ["HF_HUB_DISABLE_PROGRESS_BARS"] = "1"
os.environ["TOKENIZERS_PARALLELISM"] = "false"

logging.getLogger("sentence_transformers").setLevel(logging.ERROR)
logging.getLogger("huggingface_hub").setLevel(logging.ERROR)

import huggingface_hub
huggingface_hub.get_token = lambda *args, **kwargs: None

for _var in ("HF_TOKEN", "HUGGING_FACE_HUB_TOKEN", "HUGGINGFACE_HUB_TOKEN"):
    os.environ.pop(_var, None)
# ─────────────────────────────────────────────────────────────────────────────


from sentence_transformers import SentenceTransformer


def main():
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../processed"))
    os.makedirs(base_dir, exist_ok=True)

    csv_path = os.path.join(base_dir, "amazon_fashion.csv")
    if not os.path.exists(csv_path):
        print(f"[ERROR] {csv_path} not found. Run loader.py first:")
        print("         python data/scripts/loader.py")
        return

    df = pd.read_csv(csv_path)
    for col in ("name", "description", "category", "price", "brand"):
        if col not in df.columns:
            df[col] = ""
    df = df.fillna("")
    items = df.to_dict("records")
    print(f"[embed] Loaded {len(items)} items from {csv_path}")

    texts = [
        f"{item.get('name', '')} {item.get('description', '')} {item.get('category', '')}"
        for item in items
    ]

    print("[embed] Loading SentenceTransformer model (all-MiniLM-L6-v2)...")
    model = SentenceTransformer("paraphrase-MiniLM-L3-v2")

    print("[embed] Embedding items...")
    embeddings = model.encode(texts, batch_size=512, show_progress_bar=True, convert_to_numpy=True)

    print("[embed] Building FAISS index...")
    index = faiss.IndexFlatL2(embeddings.shape[1])
    index.add(embeddings)

    index_path = os.path.join(base_dir, "items.index")
    meta_path = os.path.join(base_dir, "items_metadata.pkl")

    faiss.write_index(index, index_path)
    metadata = {i: item for i, item in enumerate(items)}
    with open(meta_path, "wb") as f:
        pickle.dump(metadata, f)

    print(f"[embed] Done! {index.ntotal} items indexed.")
    print(f"        Index  -> {index_path}")
    print(f"        Metadata -> {meta_path}")


if __name__ == "__main__":
    main()
