# AI Agent Integration Guide

> **Status**:  COMPLETE
>
> Backend fully integrated with Emmanuel's AI agents.  
> Ready for end-to-end testing.

---

## Architecture Overview

```
Request (FastAPI)
    ↓
Router (simulate.py / recommend.py)
    ↓
Schema Validation (Pydantic)
    ↓
Agent Service (agent_service.py) ← ThreadPoolExecutor wrapper
    ↓
AI Agent (from apps/ai-agent)
    ↓
LLM (Gemini Pro via langchain)
    ↓
Response → Database Logging (background) → Client
```

---

## Environment Setup

### 1. Add Google Gemini API Key

Edit `.env`:
```
GOOGLE_API_KEY=your-actual-google-gemini-api-key-here
```

Get your key from: https://aistudio.google.com/app/apikeys

### 2. Install AI Agent Dependencies

The backend needs to import from the AI agent module. Install requirements:

```bash
# Backend venv
cd apps/backend
pip install -r requirements.txt

# If using local development (not Docker), also install AI agent deps:
pip install langchain langgraph langchain-google-genai faiss-cpu sentence-transformers
```

### 3. Verify Module Paths

In `app/services/agent_service.py`, the paths are:
- Local development: `../ai-agent`
- Docker container: `/ai-agent`

Both paths are registered, so it works in both environments.

---

## API Endpoints

### Task A: Simulate Review

**POST** `/api/v1/simulate-review`

**Request:**
```json
{
  "user_persona": {
    "user_id": "user123",
    "purchase_history": ["Infinix Hot 10", "Oraimo Powerbank"],
    "avg_rating_given": 4.2,
    "price_sensitivity": "high",
    "preferred_categories": ["Electronics", "Gadgets"],
    "is_cold_start": false
  },
  "product": {
    "name": "JBL Flip 6 Speaker",
    "category": "Electronics",
    "price": 62000,
    "brand": "JBL",
    "description": "Portable Bluetooth speaker"
  }
}
```

**Response:**
```json
{
  "predicted_rating": 3.8,
  "simulated_review": "E be like this speaker fine well well. The sound quality dey kampe with other speakers for the price range. Battery life no be joke but abeg, e no be perfect. I go recommend am to friends sha.",
  "confidence": 0.87,
  "reasoning": "User is price-conscious electronics buyer, moderately sensitive to quality. JBL Flip 6 aligns with purchase history of reliable gadgets."
}
```

**Status Codes:**
- `200` - Success
- `422` - Invalid request schema
- `504` - Agent timeout (> 60 seconds)
- `500` - Server error

---

### Task B: Get Recommendations

**POST** `/api/v1/recommend`

**Request:**
```json
{
  "user_persona": {
    "user_id": "NEW_USER_999",
    "purchase_history": [],
    "price_sensitivity": "medium",
    "preferred_categories": ["Fashion"],
    "is_cold_start": true
  },
  "top_k": 5,
  "domain": "fashion"
}
```

**Response:**
```json
{
  "recommendations": [
    {
      "item_id": "ADIDAS_ULTRABOOST",
      "item_name": "Adidas Ultraboost 23",
      "category": "Fashion",
      "score": 0.92,
      "reason": "Highly rated fashion item popular with new users. Great quality and value."
    },
    {
      "item_id": "NIKE_AIR_FORCE",
      "item_name": "Nike Air Force 1",
      "category": "Fashion",
      "score": 0.88,
      "reason": "Classic style, affordable for budget-conscious buyers. Timeless choice."
    }
  ],
  "is_cold_start": true,
  "total": 2
}
```

**Valid Domains:**
- `fashion`
- `electronics`
- `books`
- `food`

**Status Codes:**
- `200` - Success
- `422` - Invalid domain or request schema
- `504` - Agent timeout (> 60 seconds)
- `500` - Server error

---

## How the Integration Works

### Async/Thread Pool Wrapping

The AI agents are **synchronous functions**, but FastAPI is **async**. To prevent blocking:

```python
# In agent_service.py
async def run_task_a(user_persona, product):
    loop = asyncio.get_event_loop()
    with ThreadPoolExecutor() as executor:
        result = await loop.run_in_executor(executor, simulate_review, user_persona, product)
    return result
```

This runs the agent in a thread pool, keeping the async loop responsive.

### Timeout Handling

Both routers enforce a **60-second timeout**:

```python
try:
    result = await asyncio.wait_for(
        run_task_a(user_persona, product),
        timeout=60
    )
except asyncio.TimeoutError:
    raise HTTPException(status_code=504, detail="Agent took too long to respond")
```

### Background Logging

Results are logged to PostgreSQL in the background (non-blocking):

```python
background_tasks.add_task(
    log_simulation,
    user_id, product, result
)
```

---

## Testing

### Local Testing (Swagger UI)

1. Start the server:
   ```bash
   uvicorn app.main:app --reload
   ```

2. Open Swagger UI:
   ```
   http://127.0.0.1:8000/docs
   ```

3. Test Task A (`/api/v1/simulate-review`):
   - Click "Try it out"
   - Paste the example request above
   - Click "Execute"

4. Test Task B (`/api/v1/recommend`):
   - Click "Try it out"
   - Use domain: `fashion` (NOT `bags`)
   - Click "Execute"

### Curl Testing

**Task A:**
```bash
curl -X POST "http://127.0.0.1:8000/api/v1/simulate-review" \
  -H "Content-Type: application/json" \
  -d '{
    "user_persona": {
      "user_id": "user1",
      "purchase_history": ["Item1"],
      "avg_rating_given": 4.0,
      "price_sensitivity": "medium",
      "preferred_categories": ["Electronics"],
      "is_cold_start": false
    },
    "product": {
      "name": "Test Product",
      "category": "Electronics",
      "price": 5000,
      "brand": "TestBrand"
    }
  }'
```

**Task B:**
```bash
curl -X POST "http://127.0.0.1:8000/api/v1/recommend" \
  -H "Content-Type: application/json" \
  -d '{
    "user_persona": {
      "user_id": "user1",
      "purchase_history": ["Item1"],
      "price_sensitivity": "medium",
      "preferred_categories": ["Fashion"],
      "is_cold_start": false
    },
    "top_k": 5,
    "domain": "fashion"
  }'
```

---

## Database Schema

### Simulation Table
```
id          | UUID (PK)
user_id     | String
product     | JSON (product details)
result      | JSON (predicted_rating, simulated_review, confidence, reasoning)
created_at  | DateTime
```

### Recommendation Table
```
id          | UUID (PK)
user_id     | String
recommendations | JSON (list of recommendation items)
domain      | String
is_cold_start   | Boolean
created_at  | DateTime
```

### Audit Log Table
```
id          | UUID (PK)
endpoint    | String
method      | String
status_code | Int
duration_ms | Int
error_msg   | String (nullable)
created_at  | DateTime
```

---

## Troubleshooting

### "AI agent module not found"

**Cause:** Python can't find the ai-agent module.

**Fix:**
```python
# Check sys.path includes ai-agent
import sys
print(sys.path)

# Verify directory exists and has __init__.py
ls ../ai-agent/agents/__init__.py
```

### "GOOGLE_API_KEY not found" / "401 Unauthorized"

**Cause:** Missing or invalid API key.

**Fix:**
```bash
# .env file
GOOGLE_API_KEY=paste-your-actual-key-here

# Verify it's loaded
python -c "from app.config import settings; print(settings.GOOGLE_API_KEY)"
```

### "Agent took too long to respond (504)"

**Cause:** LLM call exceeded 60 seconds.

**Fix:**
- Check Gemini API is responsive: https://aistudio.google.com
- Check network connection
- Try simpler request (shorter description)

### "Invalid domain" (422)

**Cause:** Domain not in valid list.

**Fix:**
Valid domains: `fashion`, `electronics`, `books`, `food`

Not valid: `bags`, `clothing`, `tech` (use `electronics` instead)

---

## Production Deployment

### Docker

```bash
docker build -t pulseagent-backend .
docker run -e GOOGLE_API_KEY="your-key" \
           -e DATABASE_URL="your-neon-url" \
           -p 8000:8000 \
           pulseagent-backend
```

### Environment Variables Required

```
DATABASE_URL=postgresql://...
GOOGLE_API_KEY=your-api-key
ENVIRONMENT=production
SECRET_KEY=strong-random-key
```

### Monitor Logs

```bash
docker logs -f container-id
```

---

## Next Steps

1. ✅ Backend fully integrated
2. 🔄 Manual end-to-end testing
3. 🔄 Frontend integration (consume API)
4. 🔄 Load testing with realistic personas
5. 🔄 Deploy to production

---

**Questions?** Check the README.md or API_DOCUMENTATION.md

