# PulseAgent AI Backend — Multi-stage Dockerfile (Phase 8)

FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Generate Prisma client
RUN prisma generate

# Expose port
EXPOSE 8000

# Run application
CMD ["sh", "-c", "prisma db push && uvicorn app.main:app --host 0.0.0.0 --port 8000"]
