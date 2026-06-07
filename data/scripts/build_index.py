"""
build_index.py — PulseAgent AI
Rebuilds the FAISS vector index from the Amazon product dataset.

Usage:
    python data/scripts/build_index.py

Input:  data/raw/amazon_products.csv  (1.4M rows, ~360MB)
        data/raw/amazon_categories.csv
Output: data/processed/items_metadata.pkl
        data/processed/items.index         (FAISS IndexFlatIP, 384-dim)
        data/processed/tfidf_model.pkl     (fallback TF-IDF + SVD model)

The script always builds the TF-IDF fallback model.
If sentence-transformers is available and HuggingFace is reachable,
it also builds a neural FAISS index (better search quality).
"""

import os, sys, pickle, json
import numpy as np
import pandas as pd
import faiss
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]
RAW_DIR  = BASE_DIR / "data" / "raw"
OUT_DIR  = BASE_DIR / "data" / "processed"
OUT_DIR.mkdir(parents=True, exist_ok=True)

PRODUCTS_CSV   = RAW_DIR / "amazon_products.csv"
CATEGORIES_CSV = RAW_DIR / "amazon_categories.csv"

# ── Category mapping ─────────────────────────────────────────────────────────
CATEGORY_MAP = {
    # Fashion — clothing & shoes
    84: "Fashion", 90: "Fashion", 91: "Fashion", 97: "Fashion",
    100: "Fashion", 103: "Fashion", 104: "Fashion", 108: "Fashion",
    110: "Fashion", 114: "Fashion", 116: "Fashion", 118: "Fashion", 122: "Fashion",
    # Electronics — headphones, cell phones, wearables, ebook readers
    71: "Electronics", 74: "Electronics", 75: "Electronics",
    68: "Electronics", 72: "Electronics", 26: "Electronics",
    # Beauty — all sub-categories
    45: "Beauty", 47: "Beauty", 48: "Beauty", 49: "Beauty", 50: "Beauty", 53: "Beauty",
}

# NGN per USD exchange rate used to convert prices
NGN_RATE = 1600

# How many items to sample per domain
SAMPLE_SIZE = {"Fashion": 400, "Electronics": 300, "Beauty": 300}

# ── Load & filter ────────────────────────────────────────────────────────────
print("Reading Amazon products CSV in chunks …")
chunks = []
for chunk in pd.read_csv(PRODUCTS_CSV, chunksize=50_000):
    f = chunk[chunk["category_id"].isin(CATEGORY_MAP)]
    f = f[f["stars"] >= 3.8]
    f = f[f["price"] > 0]
    f = f[f["reviews"] >= 50]
    f = f.dropna(subset=["title", "price", "stars"])
    chunks.append(f)

df = pd.concat(chunks)
df["domain"] = df["category_id"].map(CATEGORY_MAP)

cats     = pd.read_csv(CATEGORIES_CSV)
cat_name = dict(zip(cats["id"], cats["category_name"]))

# Balanced sample
parts = []
for domain, n in SAMPLE_SIZE.items():
    part = (
        df[df["domain"] == domain]
        .sort_values("reviews", ascending=False)
        .head(n)
    )
    parts.append(part)
final = pd.concat(parts)
print(f"Sampled {len(final)} products  |  {dict(final['domain'].value_counts())}")

# ── Build metadata dict ───────────────────────────────────────────────────────
metadata = {}
texts    = []
for i, (_, row) in enumerate(final.iterrows()):
    ngn_price = round(float(row["price"]) * NGN_RATE)
    item = {
        "id":           str(row["asin"]),
        "name":         str(row["title"])[:120],
        "category":     row["domain"],
        "price":        ngn_price,
        "brand":        "",
        "description":  f"{cat_name.get(row['category_id'], row['domain'])} product. Highly rated on Amazon.",
        "stars":        float(row["stars"]),
        "review_count": int(row["reviews"]),
    }
    metadata[i] = item
    texts.append(f"{item['name']} {item['name']} {item['description']} {item['category']} {item['category']}")

with open(OUT_DIR / "items_metadata.pkl", "wb") as f:
    pickle.dump(metadata, f)
print("Saved items_metadata.pkl")

# ── TF-IDF + SVD index (always built) ────────────────────────────────────────
print("Building TF-IDF + SVD FAISS index (fallback) …")
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import TruncatedSVD

vectorizer = TfidfVectorizer(max_features=8000, ngram_range=(1, 2), sublinear_tf=True)
X = vectorizer.fit_transform(texts)

svd = TruncatedSVD(n_components=384, random_state=42)
E   = svd.fit_transform(X).astype(np.float32)
norms = np.linalg.norm(E, axis=1, keepdims=True)
norms[norms == 0] = 1
E = E / norms

index = faiss.IndexFlatIP(384)
index.add(E)
faiss.write_index(index, str(OUT_DIR / "items.index"))

with open(OUT_DIR / "tfidf_model.pkl", "wb") as f:
    pickle.dump({"vectorizer": vectorizer, "svd": svd}, f)
print("Saved items.index (TF-IDF/SVD) + tfidf_model.pkl")

# ── Neural index (optional — requires sentence-transformers + HuggingFace) ───
try:
    from sentence_transformers import SentenceTransformer
    print("Building neural FAISS index (sentence-transformers) …")
    model = SentenceTransformer("all-MiniLM-L6-v2")
    E_neural = model.encode(texts, convert_to_numpy=True,
                            show_progress_bar=True, batch_size=64).astype(np.float32)
    norms = np.linalg.norm(E_neural, axis=1, keepdims=True)
    norms[norms == 0] = 1
    E_neural = E_neural / norms

    idx_neural = faiss.IndexFlatIP(E_neural.shape[1])
    idx_neural.add(E_neural)
    faiss.write_index(idx_neural, str(OUT_DIR / "items.index"))
    print("Replaced items.index with neural embeddings (higher quality).")
except Exception as e:
    print(f"Neural index skipped ({e}). TF-IDF index is already in place.")

print("\nDone!  Files in", OUT_DIR)
for f in OUT_DIR.iterdir():
    print(f"  {f.name:35s}  {f.stat().st_size // 1024} KB")
