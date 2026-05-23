# 🚀 PulseAgent AI — Backend API

**Version:** 1.0.0 | **Owner:** Nwokedi Ikechukwu | **Stack:** FastAPI + Prisma + Neon PostgreSQL

---

## 📋 Quick Links

- **[Setup Guide](SETUP.md)** — Get running in 5 minutes
- **[API Documentation](API_DOCUMENTATION.md)** — Endpoint specs, request/response formats
- **[Architecture](ARCHITECTURE.md)** — System design, data flow, patterns
- **[Swagger UI](http://127.0.0.1:8000/docs)** — Interactive API explorer (when running)

---

## ⚡ What This Does

FastAPI backend for **PulseAgent AI** (BCT Hackathon 2026) with two core endpoints:

| Task  | Endpoint                       | Purpose                                      |
| ----- | ------------------------------ | -------------------------------------------- |
| **A** | `POST /api/v1/simulate-review` | Generate realistic user reviews for products |
| **B** | `POST /api/v1/recommend`       | Get personalized product recommendations     |

Both endpoints:

- ✅ Call Emmanuel's AI agents internally
- ✅ Have 60-second timeouts (prevent hanging)
- ✅ Log results to database
- ✅ Return structured JSON responses
- ✅ Include full error handling

---

## 🏗️ Tech Stack

| Layer          | Technology      | Version |
| -------------- | --------------- | ------- |
| **Framework**  | FastAPI         | 0.111.0 |
| **Server**     | Uvicorn         | 0.29.0  |
| **ORM**        | Prisma          | 0.15.0  |
| **Database**   | Neon PostgreSQL | Latest  |
| **Validation** | Pydantic v2     | 2.7.0   |
| **Testing**    | pytest          | 8.2.0   |
| **Python**     | CPython         | 3.12.7  |

---

## 🚀 Quick Start

### 1️⃣ Prerequisites

- Python 3.12+
- Neon PostgreSQL account (free at https://console.neon.tech)

### 2️⃣ Clone & Setup

```bash
cd apps/backend

# Create virtual environment
python -m venv venv
.\venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt
```

### 3️⃣ Configure Database

Create `.env` file:

```env
DATABASE_URL=postgresql://user:password@host/database
```

### 4️⃣ Run Migrations

```bash
prisma migrate dev --name init
```

### 5️⃣ Start Server

```bash
uvicorn app.main:app --reload --port 8000
```

### 6️⃣ Test

Open **[http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)** in browser

---

## 📁 Directory Structure

```
apps/backend/
├── app/
│   ├── main.py                    # ✅ FastAPI entry point
│   ├── config.py                  # ✅ Settings & env vars
│   ├── database.py                # ✅ Prisma client singleton
│   ├── routers/
│   │   ├── health.py              # ✅ GET /health
│   │   ├── simulate.py            # ✅ POST /api/v1/simulate-review
│   │   └── recommend.py           # ✅ POST /api/v1/recommend
│   ├── services/
│   │   ├── agent_service.py       # ✅ AI agent bridge
│   │   └── db_service.py          # ✅ Database operations
│   ├── schemas/
│   │   ├── request.py             # ✅ Request validation (Pydantic)
│   │   └── response.py            # ✅ Response models
│   └── utils/
│       └── constants.py           # ✅ App constants
├── prisma/
│   ├── schema.prisma              # ✅ Database schema (4 tables)
│   └── migrations/                # ✅ Migration history
├── tests/
│   └── README.md                  # Tests ready after Phase 7
├── .env                           # ⚠️  NOT in git
├── .env.example                   # ✅ Template for .env
├── requirements.txt               # ✅ All dependencies
├── Dockerfile                     # ✅ Container spec
├── SETUP.md                       # ✅ Setup instructions
├── API_DOCUMENTATION.md           # ✅ API endpoints & models
├── ARCHITECTURE.md                # ✅ System design
└── README.md                      # ✅ This file
```

---

## 🔌 API Endpoints

### Health Check

```bash
GET /health
```

Returns database & server status. Use to monitor health.

### Task A: Simulate Review

```bash
POST /api/v1/simulate-review
```

Input: User persona + product  
Output: Predicted rating (1-5), simulated review text, confidence score

### Task B: Get Recommendations

```bash
POST /api/v1/recommend
```

Input: User persona + top_k + domain (fashion/electronics/books/food)  
Output: Ranked list of products with scores & reasoning

**Full specs:** See [API_DOCUMENTATION.md](API_DOCUMENTATION.md)

---

## 📊 Database Schema

4 PostgreSQL tables (auto-created by Prisma):

| Table              | Purpose                               |
| ------------------ | ------------------------------------- |
| **User**           | Store user personas                   |
| **Simulation**     | Log Task A results (ratings, reviews) |
| **Recommendation** | Log Task B results (recommendations)  |
| **AuditLog**       | Track all API calls for monitoring    |

**Schema details:** See [ARCHITECTURE.md](ARCHITECTURE.md#database-schema)

---

## 🧪 Testing (Phase 7 — When Agents Ready)

### Run Unit Tests

```bash
pytest tests/
```

### Manual Testing

1. Open [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
2. Click endpoint
3. Click "Try it out"
4. Modify request body
5. Click "Execute"

### Test with cURL

```bash
# Health check
curl http://127.0.0.1:8000/health

# Simulate review
curl -X POST http://127.0.0.1:8000/api/v1/simulate-review \
  -H "Content-Type: application/json" \
  -d '{"user_persona": {"user_id": "u1"}, "product": {"product_id": "p1"}}'
```

---

## 🐳 Docker

### Build Container

```bash
docker build -t pulseagent-backend .
```

### Run Container

```bash
docker run -e DATABASE_URL="postgresql://..." -p 8000:8000 pulseagent-backend
```

### Docker Compose (from root)

```bash
docker-compose up
```

---

## 📝 Development

### Making Changes

1. Edit files in `app/`
2. Server auto-reloads (thanks to `--reload`)
3. Check errors in terminal

### Database Changes

```bash
# Edit prisma/schema.prisma
# Then run:
prisma migrate dev --name your_change_name
```

### View Database

```bash
prisma studio
# Opens GUI at http://localhost:5555
```

---

## 🚨 Troubleshooting

| Issue                            | Solution                                 |
| -------------------------------- | ---------------------------------------- |
| "No module named fastapi"        | Activate venv: `.\venv\Scripts\activate` |
| "Connection refused" to DB       | Check DATABASE_URL in .env               |
| "relation 'User' does not exist" | Run migrations: `prisma migrate dev`     |
| Port 8000 in use                 | Use different port: `--port 8001`        |

**More help:** See [SETUP.md](SETUP.md#troubleshooting)

---

## 📦 Dependencies

**Core:**

- `fastapi` — Web framework
- `uvicorn` — ASGI server
- `prisma` — Database ORM

**Validation:**

- `pydantic` — Request/response validation

**Database:**

- `neon` — Serverless PostgreSQL

**Testing:**

- `pytest` — Test framework (Phase 7)

**All versions:** See [requirements.txt](requirements.txt)

---

## 📖 Documentation

| Document                                     | Purpose                             |
| -------------------------------------------- | ----------------------------------- |
| [SETUP.md](SETUP.md)                         | Step-by-step setup guide            |
| [API_DOCUMENTATION.md](API_DOCUMENTATION.md) | Endpoint specs & examples           |
| [ARCHITECTURE.md](ARCHITECTURE.md)           | System design & patterns            |
| Swagger UI                                   | Interactive API explorer at `/docs` |

---

## 🎯 Implementation Status

| Phase   | Status      | Details                               |
| ------- | ----------- | ------------------------------------- |
| Phase 0 | ✅ Complete | Neon DB, venv, .env configured        |
| Phase 1 | ✅ Complete | File structure created (25+ files)    |
| Phase 2 | ✅ Complete | Prisma schema migrated to Neon        |
| Phase 3 | ✅ Complete | FastAPI running, endpoints responding |
| Phase 4 | ✅ Complete | Pydantic schemas validated            |
| Phase 5 | ✅ Complete | Agent service bridge ready            |
| Phase 6 | ✅ Complete | All 3 endpoints fully implemented     |
| Phase 7 | ⏳ Waiting  | Unit tests (need agents ready first)  |
| Phase 8 | ✅ Done     | Docker build works                    |
| Phase 9 | ✅ Complete | Comprehensive documentation           |

---

## 🔮 Next Steps

1. **Verify Agents:** Emmanuel finalizes AI agents
2. **Integrate Agents:** Connect agents to agent_service.py
3. **Run Tests:** Execute Phase 7 test suite
4. **Deploy:** Push to production (Fly.io, Railway, etc)

---

## 👤 Contact

**Backend Owner:** Nwokedi Ikechukwu  
**AI Agents Owner:** Emmanuel/Iseoluwa  
**Hackathon:** BCT Hackathon 2026

---

**Ready to test?** See [SETUP.md](SETUP.md) to get started! 🚀

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
│ └── nginx.conf # Reverse proxy (optional, for polish)
└── postgres/
└── init.sql # DB init script

```

---

## Dataset Download Scripts (`data/`)

```

data/
├── scripts/
│ ├── download_amazon.py # Downloads Amazon Reviews 2023 subset
│ ├── download_yelp.py # Instructions to get Yelp dataset
│ └── download_goodreads.py # Goodreads dataset download
├── raw/ # Downloaded raw files (gitignored)
└── processed/ # Cleaned data + FAISS indexes

````

```python
# data/scripts/download_amazon.py
from datasets import load_dataset
# Download a small subset for demo
ds = load_dataset("McAuley-Lab/Amazon-Reviews-2023",
                  "raw_review_Clothing_Shoes_and_Jewelry",
                  split="full", trust_remote_code=True)
ds.to_csv("data/raw/amazon_fashion.csv")
print(f"Downloaded {len(ds)} reviews")
````

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
