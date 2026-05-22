# ⚡ Backend API — Nwokedi's Domain
> **Nwokedi Ikechukwu** | FastAPI Backend + Docker Infrastructure

---

## Your Mission
You own the entire backend and deployment infrastructure. Every API call from the frontend goes through you. You also call Emmanuel's AI agent module internally. You make the system containerised and submittable.

---

## Your Deliverables

1. **FastAPI application** with Task A and Task B endpoints
2. **Docker + docker-compose** — one command launches the entire stack
3. **Database** — SQLite (fast) or PostgreSQL for storing personas and results
4. **Dataset download scripts** in `data/`
5. **Clean API documentation** at `/docs` (Swagger auto-generated)

---

## Directory Structure

```
apps/backend/
├── app/
│   ├── main.py                  # FastAPI app entry point
│   ├── config.py                # Settings from .env
│   ├── database.py              # DB connection + SQLAlchemy setup
│   ├── routers/
│   │   ├── simulate.py          # POST /api/v1/simulate-review (Task A)
│   │   ├── recommend.py         # POST /api/v1/recommend (Task B)
│   │   └── health.py            # GET /health
│   ├── schemas/
│   │   ├── request.py           # Pydantic request models
│   │   └── response.py          # Pydantic response models
│   ├── models/
│   │   └── user_profile.py      # SQLAlchemy DB model
│   └── services/
│       ├── agent_service.py     # Calls Emmanuel's AI agent
│       └── cache_service.py     # Simple in-memory cache
├── tests/
│   ├── test_simulate.py
│   └── test_recommend.py
├── Dockerfile
├── requirements.txt
└── README.md
```

---

## Tech Stack
| Tool | Purpose |
|---|---|
| **FastAPI** | REST API framework |
| **SQLAlchemy** | ORM |
| **SQLite / PostgreSQL** | Database |
| **Pydantic v2** | Request/response validation |
| **Uvicorn** | ASGI server |
| **httpx** | Async HTTP client (for testing) |
| **pytest** | Testing |

---

## API Endpoints to Build

### `POST /api/v1/simulate-review` (Task A)
```python
# Request body
{
  "user_persona": {
    "user_id": "string",
    "purchase_history": ["item1", "item2"],
    "avg_rating_given": 3.8,
    "price_sensitivity": "high|medium|low",
    "preferred_categories": ["footwear"]
  },
  "product": {
    "name": "string",
    "category": "string",
    "price": 45000,
    "brand": "string",
    "description": "string"
  }
}
# Response
{
  "predicted_rating": 3.5,
  "simulated_review": "Honestly, e good o but...",
  "confidence": 0.82,
  "reasoning": "User is price-sensitive..."
}
```

### `POST /api/v1/recommend` (Task B)
```python
# Request body
{
  "user_persona": {
    "user_id": "string",
    "is_cold_start": false,
    "purchase_history": [],
    "context": "looking for evening shoes for owambe"
  },
  "top_k": 10,
  "domain": "fashion|electronics|books|food"
}
# Response
{
  "recommendations": [
    {
      "item_id": "string",
      "item_name": "string",
      "category": "string",
      "score": 0.95,
      "reason": "Based on your preference for..."
    }
  ],
  "is_cold_start": false,
  "total": 10
}
```

### `GET /health`
```json
{ "status": "ok", "version": "1.0.0" }
```

---

## `app/main.py` Skeleton

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import simulate, recommend, health
from app.config import settings

app = FastAPI(
    title="PurseAgent AI",
    description="Next-Best-Action Customer Intelligence Agent",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(simulate.router, prefix="/api/v1")
app.include_router(recommend.router, prefix="/api/v1")
```

---

## Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .

EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
```

---

## `requirements.txt`

```
fastapi==0.111.0
uvicorn[standard]==0.29.0
pydantic==2.7.0
pydantic-settings==2.2.0
sqlalchemy==2.0.30
aiosqlite==0.20.0
python-dotenv==1.0.0
httpx==0.27.0
pytest==8.2.0
pytest-asyncio==0.23.0
```

---

## Setup (Local Dev)

```bash
cd apps/backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Create .env from root .env.example
cp ../../.env.example .env

# Run the API
uvicorn app.main:app --reload --port 8000

# API docs at: http://localhost:8000/docs
```

---

## Docker Infrastructure (Root Level)

You also own the root `docker-compose.yml` and `infra/` directory.

### `infra/` structure:
```
infra/
├── nginx/
│   └── nginx.conf      # Reverse proxy (optional, for polish)
└── postgres/
    └── init.sql        # DB init script
```

---

## Dataset Download Scripts (`data/`)

```
data/
├── scripts/
│   ├── download_amazon.py      # Downloads Amazon Reviews 2023 subset
│   ├── download_yelp.py        # Instructions to get Yelp dataset
│   └── download_goodreads.py   # Goodreads dataset download
├── raw/                        # Downloaded raw files (gitignored)
└── processed/                  # Cleaned data + FAISS indexes
```

```python
# data/scripts/download_amazon.py
from datasets import load_dataset
# Download a small subset for demo
ds = load_dataset("McAuley-Lab/Amazon-Reviews-2023", 
                  "raw_review_Clothing_Shoes_and_Jewelry",
                  split="full", trust_remote_code=True)
ds.to_csv("data/raw/amazon_fashion.csv")
print(f"Downloaded {len(ds)} reviews")
```

---

## Git Workflow
```bash
git checkout -b feat/backend
# Work in apps/backend/ and infra/ and data/
git add apps/backend/ infra/ data/ docker-compose.yml .env.example
git commit -m "feat(backend): add simulate-review and recommend endpoints"
git push origin feat/backend
# Open PR to main when done
```
