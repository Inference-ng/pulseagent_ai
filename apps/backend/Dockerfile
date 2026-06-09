# ── Backend Dockerfile  (AWS Edition) ────────────────────────────────────────
FROM python:3.11-slim

WORKDIR /app

# ── System deps ───────────────────────────────────────────────────────────────
RUN apt-get update && \
    apt-get install -y --no-install-recommends build-essential curl && \
    rm -rf /var/lib/apt/lists/*

# ── Python deps ───────────────────────────────────────────────────────────────
COPY apps/backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ── Pre-download sentence-transformers model ──────────────────────────────────
RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2')" \
    || echo "[WARN] Model pre-download failed — will download at runtime"

# ── Application code ──────────────────────────────────────────────────────────
COPY apps/backend/ .
COPY apps/ai-agent/ /ai-agent
# NOTE: data/processed/ is NOT copied — artifacts are pulled from S3 at startup

RUN prisma generate

# ── Environment defaults ──────────────────────────────────────────────────────
ENV DISABLE_NEURAL_SEARCH=0
ENV HF_HUB_DISABLE_PROGRESS_BARS=1
ENV TOKENIZERS_PARALLELISM=false
ENV TRANSFORMERS_VERBOSITY=error
# Point FAISSStore to the correct path inside the container
ENV FAISS_DATA_DIR=/app/data/processed

# ── Health check ──────────────────────────────────────────────────────────────
HEALTHCHECK --interval=30s --timeout=10s --start-period=120s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

EXPOSE 8000

# prisma db push runs migrations; uvicorn starts the API
CMD ["sh", "-c", "prisma db push && uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 2"]
