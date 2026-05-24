FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y build-essential && rm -rf /var/lib/apt/lists/*

# Install backend deps
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Pre-cache the sentence transformer model
RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2')"

# Copy backend code
COPY . .

# Copy ai-agent code so agent_service.py can find it
COPY ../ai-agent /ai-agent

# Copy FAISS data so faiss_store.py can find it
COPY ../../data /app/data

# Generate Prisma client
RUN prisma generate

EXPOSE 8000
CMD ["sh", "-c", "prisma db push && uvicorn app.main:app --host 0.0.0.0 --port 8000"]