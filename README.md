# 🤖 PurseAgent AI — BCT Hackathon 2026

> **Next-Best-Action Customer Intelligence Agent**  
> A dual-task LLM system for user modeling and personalized recommendation — built for the Bluechip Tech Hackathon 2026.



---

## 🎯 What We Built

**PurseAgent AI** is an intelligent customer agent that:

- **Task A (User Modeling):** Given a user persona and product details, simulates realistic star ratings and written reviews — capturing the user's tone, preferences, and behavioral patterns.
- **Task B (Recommendation):** Given a user persona, returns a ranked, personalized list of product/item recommendations with contextual reasoning — handling cold-start users and cross-domain scenarios.

The system is trained on real-world behavioral data from **Yelp**, **Amazon Reviews**, and **Goodreads**, and is contextualised to sound authentically Nigerian for the bonus criterion.

---

## 🏗️ Repository Structure (Monorepo)

```
purseagent-ai/
├── apps/
│   ├── frontend/          # React demo dashboard (Victor)
│   ├── backend/           # FastAPI REST API (Nwokedi)
│   └── ai-agent/          # LangChain/LangGraph agents (Emmanuel)
├── data/                  # Dataset download & preprocessing scripts
├── docs/                  # Solution paper, architecture diagrams
├── infra/                 # Docker configuration
├── docker-compose.yml     # One-command full-stack launch
├── README.md              # ← You are here
└── prompt.md              # Coding agent task prompts
```

---

## 👥 Team

| Member | Role | Domain |
|---|---|---|
| **Emmanuel** (Elebiemayo Iseoluwa) | AI/ML Engineer | `apps/ai-agent/` |
| **Nwokedi Ikechukwu** | Backend Engineer | `apps/backend/` + `infra/` |
| **Victor Chukwuebuka** | Frontend Engineer | `apps/frontend/` |
| **David Aborowa** | Solution Paper, Pitch Deck, Security | `docs/` |

---

## 🚀 Quick Start (Run Everything)

### Prerequisites
- Docker Desktop installed and running
- Git

### 1. Clone the repo
```bash
git clone https://github.com/purseagent-bct/purseagent-ai.git
cd purseagent-ai
```

### 2. Set up environment variables
```bash
cp .env.example .env
# Edit .env — add your API keys (see .env.example for required keys)
```

### 3. Launch the full stack
```bash
docker-compose up --build
```

### 4. Access the services
| Service | URL |
|---|---|
| Frontend Dashboard | http://localhost:3000 |
| Backend API | http://localhost:8000 |
| API Docs (Swagger) | http://localhost:8000/docs |

---

## 📡 API Endpoints

### Task A — Simulate Review
```http
POST /api/v1/simulate-review
Content-Type: application/json

{
  "user_persona": {
    "user_id": "emmanuel_01",
    "purchase_history": ["Nike Air Max", "Adidas Slides"],
    "avg_rating_given": 3.8,
    "price_sensitivity": "high",
    "preferred_categories": ["footwear", "sportswear"]
  },
  "product": {
    "name": "Puma RS-X Sneakers",
    "category": "footwear",
    "price": 45000,
    "brand": "Puma"
  }
}
```

**Response:**
```json
{
  "predicted_rating": 3.5,
  "simulated_review": "Honestly, e good o but the price no balance for what you're getting...",
  "confidence": 0.82,
  "reasoning": "User is price-sensitive; delivery friction noted in past behavior"
}
```

### Task B — Get Recommendations
```http
POST /api/v1/recommend
Content-Type: application/json

{
  "user_persona": {
    "user_id": "chioma_02",
    "is_cold_start": false,
    "context": "looking for evening wear for an owambe"
  },
  "top_k": 10,
  "domain": "fashion"
}
```

---

## 📊 Datasets Used

| Dataset | Source | Usage |
|---|---|---|
| Amazon Reviews | [Hugging Face](https://huggingface.co/datasets/McAuley-Lab/Amazon-Reviews-2023) | Primary training + Task A/B |
| Yelp Dataset | [yelp.com/dataset](https://www.yelp.com/dataset) | Cross-domain cold-start |
| Goodreads | [UCSD Book Graph](https://mengtingwan.github.io/data/goodreads.html) | Cross-domain recommendation |

---

## 🐳 Containerisation

Each service has its own `Dockerfile`. The root `docker-compose.yml` orchestrates them all:

```yaml
services:
  frontend:   port 3000
  backend:    port 8000
  ai-agent:   internal service (called by backend)
  db:         PostgreSQL on port 5432
```

---

## 📝 Submission Checklist

- [ ] Task A agent deployed and accessible
- [ ] Task B agent deployed and accessible
- [ ] Solution paper (4–8 pages) PDF ready
- [ ] GitHub repo clean, documented, reproducible
- [ ] All three submitted via [submission form](https://forms.gle/...) before midnight 24 May 2026
- [ ] README reviewed by all team members

---

## 🧠 Tech Stack

| Layer | Technology |
|---|---|
| AI Agent | LangChain, LangGraph, FAISS |
| LLM | Llama 3 (via Ollama) / GPT-4o-mini |
| Backend | FastAPI, Python 3.11, SQLAlchemy |
| Database | PostgreSQL |
| Frontend | React 18, Vite, TailwindCSS |
| Containerisation | Docker, Docker Compose |
| Datasets | Amazon Reviews 2023, Yelp, Goodreads |

---

## 📄 Documentation

- [`docs/solution-paper.md`](./docs/solution-paper.md) — Full solution paper
- [`docs/architecture.md`](./docs/architecture.md) — System architecture
- [`apps/frontend/README.md`](./apps/frontend/README.md) — Frontend setup
- [`apps/backend/README.md`](./apps/backend/README.md) — Backend setup
- [`apps/ai-agent/README.md`](./apps/ai-agent/README.md) — AI agent setup
- [`prompt.md`](./prompt.md) — Coding agent task prompts

---

*Built with ❤️ for the BCT Hackathon 2026 — Bluechip Tech*