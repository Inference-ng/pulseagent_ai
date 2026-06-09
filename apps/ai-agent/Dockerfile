# ── AI-Agent Dockerfile  (AWS Edition) ───────────────────────────────────────
# Base: python:3.11-slim
# Notable changes from Render version:
#   - sentence-transformers IS installed (neural search enabled)
#   - all-MiniLM-L6-v2 model pre-downloaded into the image layer
#     so cold-start latency is < 1 s instead of ~30 s
#   - boto3 installed for S3 artifact download
#   - FAISS artifacts are NOT bundled in the image —
#     they are pulled from S3 at container startup via FAISSStore._download_from_s3()
#   - DISABLE_NEURAL_SEARCH defaults to "0" (neural mode ON)

FROM python:3.11-slim

WORKDIR /app

# ── System deps ───────────────────────────────────────────────────────────────
RUN apt-get update && \
    apt-get install -y --no-install-recommends build-essential curl && \
    rm -rf /var/lib/apt/lists/*

# ── Python deps ───────────────────────────────────────────────────────────────
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ── Pre-download sentence-transformers model ──────────────────────────────────
# Baked into the image layer → zero network calls at runtime
RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2')" \
    || echo "[WARN] Model pre-download failed — will download at runtime"

# ── Application code ──────────────────────────────────────────────────────────
COPY . .

# ── Environment defaults (override in ECS task definition / docker run) ───────
ENV DISABLE_NEURAL_SEARCH=0
ENV HF_HUB_DISABLE_PROGRESS_BARS=1
ENV TOKENIZERS_PARALLELISM=false
ENV TRANSFORMERS_VERBOSITY=error

# ── Health check ──────────────────────────────────────────────────────────────
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD python -c "from memory.faiss_store import FAISSStore; s=FAISSStore(); exit(0 if s.total_items > 0 else 1)"

# ── Default: keep alive (backend calls into this container via RPC / shared code)
CMD ["tail", "-f", "/dev/null"]
