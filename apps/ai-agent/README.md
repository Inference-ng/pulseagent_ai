# 🤖 AI Agent — Emmanuel's Domain
> **Elebiemayo Iseoluwa Emmanuel** | LangChain/LangGraph Agent Core

---

## Your Mission
Build the core intelligence of PulseAgent AI. You own the two LangGraph agents that power both hackathon tasks. The backend calls your agent as a Python module — your output quality determines our score.

---

## Your Deliverables

### Task A Agent — User Modeling (`agents/user_modeling_agent.py`)
- Accept a `UserPersona` + `Product` as input
- Return a simulated `star_rating` (1–5) + `review_text`
- Review must capture tone, price sensitivity, and behavioural nuance
- **Bonus**: Responses must sound authentically Nigerian

### Task B Agent — Recommendation (`agents/recommendation_agent.py`)
- Accept a `UserPersona` + optional `context` string as input
- Return a ranked list of top-K items with reasoning per item
- Handle **cold-start** users (no history) using demographic + context fallback
- Handle **cross-domain**: if user likes sneakers → also recommend sportswear

---

## Directory Structure

```
apps/ai-agent/
├── agents/
│   ├── user_modeling_agent.py     # Task A: review + rating simulation
│   ├── recommendation_agent.py    # Task B: ranked recommendations
│   └── base_agent.py              # Shared LangGraph base config
├── memory/
│   ├── faiss_store.py             # FAISS vector store for user embeddings
│   └── user_memory.py             # User profile builder from history
├── data/
│   ├── loader.py                  # Load Amazon / Yelp / Goodreads datasets
│   ├── preprocessor.py            # Clean + chunk data into embeddings
│   └── embed.py                   # Embed items into FAISS index
├── prompts/
│   ├── task_a_prompt.py           # System + human prompt templates (Task A)
│   ├── task_b_prompt.py           # System + human prompt templates (Task B)
│   └── nigerian_context.py        # Nigerian tone layer (bonus marks)
├── schemas/
│   └── models.py                  # Pydantic models: UserPersona, Product, etc.
├── tests/
│   ├── test_user_modeling.py
│   └── test_recommendation.py
├── Dockerfile
├── requirements.txt
└── README.md
```

---

## Tech Stack
| Tool | Purpose |
|---|---|
| **LangGraph** | Agent orchestration with state machine |
| **LangChain** | LLM chains, prompts, memory |
| **FAISS** | Vector store for item + user embeddings |
| **Llama 3 (Ollama)** or **GPT-4o-mini** | LLM backbone |
| **Sentence Transformers** | Embedding model (`all-MiniLM-L6-v2`) |
| **Pydantic v2** | Schema validation |
| **Datasets (HuggingFace)** | Amazon Reviews 2023 loader |

---

## Setup

```bash
cd apps/ai-agent
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Download and preprocess datasets
python data/loader.py
python data/preprocessor.py
python data/embed.py   # builds FAISS index

# Run tests
pytest tests/
```

---

## `requirements.txt`

```
langchain==0.2.0
langgraph==0.1.0
langchain-community==0.2.0
langchain-openai==0.1.0
faiss-cpu==1.8.0
sentence-transformers==3.0.0
pydantic==2.7.0
datasets==2.19.0
pandas==2.2.0
numpy==1.26.0
python-dotenv==1.0.0
pytest==8.2.0
```

---

## Key Implementation Details

### Nigerian Context Prompt (BONUS MARKS)
Your `nigerian_context.py` must inject this into every review prompt:
```
You are a Nigerian e-commerce shopper. Write the way Nigerians actually talk:
- Use common Nigerian expressions ("e go do", "this one na", "abeg")
- Reference naira (₦), Lagos/Abuja, Jumia, Konga
- Be direct — Nigerians don't sugarcoat bad products
- Price-sensitive users complain about shipping fees
```

### Cold-Start Strategy (25pts in Task B)
When `is_cold_start=True` (no purchase history):
1. Use **demographic signals** (location, age group if available)
2. Use **contextual query** ("looking for owambe shoes") → semantic search FAISS
3. Use **category popularity** fallback (top items in requested domain)
4. Return confidence score to reflect uncertainty

### FAISS Index Build
```python
# embed.py — builds the searchable item index
from sentence_transformers import SentenceTransformer
import faiss, pickle

model = SentenceTransformer('all-MiniLM-L6-v2')
# Load Amazon products...
embeddings = model.encode(product_descriptions)
index = faiss.IndexFlatL2(embeddings.shape[1])
index.add(embeddings)
faiss.write_index(index, 'data/processed/items.index')
```

---

## Interface Contract (Backend calls your code like this)

```python
# Task A
from agents.user_modeling_agent import simulate_review
result = simulate_review(user_persona=persona_dict, product=product_dict)
# Returns: {"predicted_rating": 4.0, "simulated_review": "...", "confidence": 0.85}

# Task B
from agents.recommendation_agent import get_recommendations
result = get_recommendations(user_persona=persona_dict, top_k=10, domain="fashion")
# Returns: {"recommendations": [{"item_id": "...", "score": 0.92, "reason": "..."}]}
```

---

## Scoring Focus
- **ROUGE/BERTScore** → make reviews long enough (3–5 sentences) and semantically rich
- **RMSE** → calibrate rating predictions using user's historical average as anchor
- **Behavioural Fidelity** → the review must reflect the user persona accurately
- **NDCG@10** → ensure your ranked list puts the best items first

---

## Git Workflow
```bash
git checkout -b feat/ai-agent
# Work in apps/ai-agent/
git add apps/ai-agent/
git commit -m "feat(ai-agent): implement Task A user modeling agent"
git push origin feat/ai-agent
# Open PR to main when done
```
