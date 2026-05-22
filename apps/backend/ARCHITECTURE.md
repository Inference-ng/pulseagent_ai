# Backend Architecture & System Design

**Overview:** Production-ready FastAPI backend for PurseAgent AI using serverless PostgreSQL and modern Python patterns.

---

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Frontend (Vue/React)                    │
└────────────────────────┬────────────────────────────────────┘
                         │ HTTP/REST
                         ↓
┌─────────────────────────────────────────────────────────────┐
│                   FastAPI Application                       │
│  ┌───────────────────────────────────────────────────────┐  │
│  │ Routers (app/routers/)                               │  │
│  │  • health.py     — Health check & DB status          │  │
│  │  • simulate.py   — Task A: Review simulation         │  │
│  │  • recommend.py  — Task B: Recommendations           │  │
│  └─────────────────┬─────────────────────────────────────┘  │
│                    │                                         │
│  ┌─────────────────↓─────────────────────────────────────┐  │
│  │ Services (app/services/)                             │  │
│  │  • agent_service.py  — Bridge to AI agents           │  │
│  │  • db_service.py     — Database operations           │  │
│  └─────────────────┬─────────────────────────────────────┘  │
│                    │                                         │
│  ┌─────────────────↓─────────────────────────────────────┐  │
│  │ Schemas (app/schemas/)                               │  │
│  │  • request.py    — Pydantic request validation       │  │
│  │  • response.py   — Pydantic response models          │  │
│  └─────────────────┬─────────────────────────────────────┘  │
│                    │                                         │
│  ┌─────────────────↓─────────────────────────────────────┐  │
│  │ Database Layer (app/database.py)                     │  │
│  │  • Prisma client singleton                           │  │
│  │  • Connection pooling                                │  │
│  └─────────────────┬─────────────────────────────────────┘  │
└────────────────────┼──────────────────────────────────────────┘
                     │
                     ↓
┌─────────────────────────────────────────────────────────────┐
│         Neon PostgreSQL (Serverless, Auto-scaling)         │
│  • 4 tables: User, Simulation, Recommendation, AuditLog   │
│  • Connection pooling enabled                             │
│  • Automatic backups & replicas                           │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│              AI Agents (apps/ai-agent/)                     │
│  • user_modeling_agent.py   — Task A: Generate reviews     │
│  • recommendation_agent.py  — Task B: Rank products        │
│  • (Managed by Emmanuel/Iseoluwa)                          │
└─────────────────────────────────────────────────────────────┘
```

---

## Directory Structure

```
apps/backend/
├── app/
│   ├── main.py                    # FastAPI application entry point
│   ├── config.py                  # Settings & environment variables
│   ├── database.py                # Prisma client singleton
│   │
│   ├── routers/
│   │   ├── health.py              # GET /health
│   │   ├── simulate.py            # POST /api/v1/simulate-review
│   │   └── recommend.py           # POST /api/v1/recommend
│   │
│   ├── services/
│   │   ├── agent_service.py       # AI agent bridge
│   │   └── db_service.py          # Database operations
│   │
│   ├── schemas/
│   │   ├── request.py             # Request validation models
│   │   └── response.py            # Response models
│   │
│   └── utils/
│       └── constants.py           # App constants (domains, timeouts)
│
├── prisma/
│   ├── schema.prisma              # Database schema definition
│   └── migrations/                # Migration history
│
├── tests/
│   ├── test_health.py             # (To be added with agents)
│   ├── test_simulate.py           # (To be added with agents)
│   └── test_recommend.py          # (To be added with agents)
│
├── .env                           # Environment variables
├── requirements.txt               # Python dependencies
├── Dockerfile                     # Container specification
├── docker-compose.yml             # (In root project)
└── README.md                      # Backend setup guide
```

---

## Data Flow

### Task A: Review Simulation

```
1. Client sends POST /api/v1/simulate-review
   ↓
2. FastAPI validates request with SimulateReviewRequest schema
   ↓
3. Router extracts user_persona and product
   ↓
4. Service calls run_task_a(user_persona, product)
   ↓
5. AI Agent processes data (60-second timeout)
   ↓
6. Agent returns: {predicted_rating, simulated_review, confidence, reasoning}
   ↓
7. Router validates response with SimulateReviewResponse schema
   ↓
8. Response sent to client (200 OK)
   ↓
9. [Background] Log result to Simulation table
   ↓
10. [Background] Log audit entry to AuditLog table
```

### Task B: Recommendations

```
1. Client sends POST /api/v1/recommend
   ↓
2. FastAPI validates request with RecommendRequest schema
   ↓
3. Router validates domain in VALID_DOMAINS (422 if invalid)
   ↓
4. Service calls run_task_b(user_persona, top_k, domain)
   ↓
5. AI Agent ranks products (60-second timeout)
   ↓
6. Agent returns: {recommendations[], is_cold_start, total}
   ↓
7. Router validates response with RecommendResponse schema
   ↓
8. Response sent to client (200 OK)
   ↓
9. [Background] Log result to Recommendation table
   ↓
10. [Background] Log audit entry to AuditLog table
```

---

## Key Design Patterns

### 1. Layered Architecture
- **Routers** → Handle HTTP requests, error handling
- **Services** → Business logic, agent coordination
- **Schemas** → Request/response validation
- **Database** → Data persistence via Prisma

**Benefit:** Clean separation of concerns, easy to test

### 2. Background Tasks
- Logging is non-blocking
- `BackgroundTasks.add_task()` runs after response
- Response returns immediately (user doesn't wait)

```python
# Response returns immediately
return response

# Logging happens in background
background_tasks.add_task(log_simulation, ...)
```

### 3. Timeout Handling
- All agent calls wrap in `asyncio.wait_for(timeout=60)`
- Prevents hanging requests
- Returns 504 if agent exceeds timeout

```python
try:
    result = await asyncio.wait_for(
        run_task_a(...),
        timeout=AGENT_TIMEOUT
    )
except asyncio.TimeoutError:
    raise HTTPException(status_code=504)
```

### 4. Request Validation
- Pydantic v2 automatically validates all inputs
- Schema docstrings generate OpenAPI schema
- Invalid requests return 422 with error details

```python
@app.post("/api/v1/simulate-review")
async def simulate_review(req: SimulateReviewRequest):
    # Pydantic validates automatically
```

### 5. Database Connection Pooling
- Single Prisma client instance
- Connection pool managed automatically
- Graceful shutdown on app close

```python
@app.on_event("startup")
async def startup_event():
    await connect_db()

@app.on_event("shutdown")
async def shutdown_event():
    await disconnect_db()
```

---

## Error Handling Strategy

### 1. Input Validation (400s)
- **422:** Invalid request format/domain
- **Handled by:** Pydantic schemas

### 2. Server Errors (500s)
- **500:** Unexpected error during processing
- **Handled by:** Try/except blocks in routers

### 3. Timeout Errors (504)
- **504:** Agent exceeded 60-second timeout
- **Handled by:** asyncio.wait_for()

### 4. Service Errors (503)
- **503:** Database unavailable
- **Handled by:** Health check endpoint

---

## Performance Considerations

### 1. Async/Await
- All I/O operations are async
- Allows handling multiple requests concurrently
- Uvicorn manages worker pool

### 2. Database Indexing
```sql
-- Simulate table
CREATE INDEX ON "Simulation"(user_id);

-- Recommendation table
CREATE INDEX ON "Recommendation"(user_id, domain);
```

### 3. Connection Pooling
- Prisma uses connection pooling
- Neon handles connection management
- Max 10 concurrent connections (dev)

### 4. Response Caching (Future)
- Could cache recommendations by (user_id, domain)
- Cold-start detection prevents stale data
- TTL: 24 hours

---

## Security Considerations

### Currently Implemented
- ✅ CORS enabled (configurable origins)
- ✅ Request validation (Pydantic)
- ✅ Database connection via TLS

### To Implement (Production)
- [ ] API key authentication
- [ ] JWT token validation
- [ ] Rate limiting per user
- [ ] Input sanitization for SQL injection
- [ ] HTTPS/TLS enforcement
- [ ] Audit logging for compliance
- [ ] Encryption at rest for sensitive data

---

## Monitoring & Logging

### Audit Log Table
Tracks every API call:
```
endpoint      | method | status_code | duration_ms | error_msg | created_at
/api/v1/...   | POST   | 200         | 1234        | null      | 2026-05-22
```

### Application Logs
- Server startup/shutdown messages
- Database connection status
- Error tracebacks (in development)

### Metrics (Future)
- [ ] Request latency histogram
- [ ] Agent timeout frequency
- [ ] Database query performance
- [ ] Error rate by endpoint

---

## Testing Strategy

### Unit Tests (Phase 7)
- Mock AI agents
- Test request validation
- Test error handling
- Test response schemas

### Integration Tests (Phase 8)
- Real agents + real database
- End-to-end request/response
- Performance benchmarks

### Load Testing (Future)
- Simulate concurrent users
- Measure agent timeout behavior
- Database pool exhaustion

---

## Deployment Options

### Option 1: Docker Container (Recommended for Hackathon)
```bash
docker build -t purseagent-backend .
docker run -e DATABASE_URL=... -p 8000:8000 purseagent-backend
```

### Option 2: Fly.io / Render / Railway
- Git push deployment
- Automatic scaling
- Built-in PostgreSQL

### Option 3: AWS Lambda
- Serverless option
- Auto-scaling
- Lower cost for variable load

---

## Dependencies

### Core
- **FastAPI 0.111.0** — Web framework
- **Uvicorn 0.29.0** — ASGI server
- **Prisma 0.15.0** — ORM

### Data Validation
- **Pydantic 2.7.0** — Request/response validation

### Database
- **Neon PostgreSQL** — Serverless database
- **psycopg** — PostgreSQL adapter (via Prisma)

### Testing (Future)
- **pytest** — Test framework
- **pytest-asyncio** — Async test support
- **httpx** — HTTP client for testing

---

## Future Enhancements

- [ ] Implement caching layer (Redis)
- [ ] Add GraphQL endpoint
- [ ] Implement webhook callbacks
- [ ] Add batch operations endpoint
- [ ] Real-time updates via WebSocket
- [ ] Admin dashboard for monitoring
- [ ] A/B testing framework
- [ ] ML model versioning
