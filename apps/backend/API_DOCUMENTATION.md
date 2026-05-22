# PurseAgent AI — Backend API Documentation

**Version:** 1.0.0  
**Environment:** FastAPI + Prisma ORM + Neon PostgreSQL  
**Last Updated:** May 22, 2026

---

## Table of Contents

1. [Overview](#overview)
2. [Quick Start](#quick-start)
3. [API Endpoints](#api-endpoints)
4. [Request/Response Models](#requestresponse-models)
5. [Error Handling](#error-handling)
6. [Database Schema](#database-schema)
7. [Authentication (Future)](#authentication-future)

---

## Overview

The PurseAgent AI backend provides two core APIs for the BCT Hackathon 2026:

- **Task A (Simulate):** Generate realistic user reviews and ratings for products
- **Task B (Recommend):** Provide personalized product recommendations based on user profile

### Key Features

- ✅ Production-grade FastAPI application
- ✅ Serverless PostgreSQL (Neon) for scalability
- ✅ Type-safe ORM (Prisma) with auto-migrations
- ✅ Comprehensive request validation (Pydantic v2)
- ✅ 60-second agent timeouts to prevent hanging
- ✅ Background logging and audit trails
- ✅ CORS enabled for frontend integration
- ✅ Auto-generated Swagger UI at `/docs`

---

## Quick Start

### Prerequisites

- Python 3.12+
- Virtual environment (venv)
- Neon PostgreSQL account + connection string

### Installation

```bash
# 1. Clone and navigate to backend
cd apps/backend

# 2. Create virtual environment
python -m venv venv
.\venv\Scripts\activate  # Windows
source venv/bin/activate  # macOS/Linux

# 3. Install dependencies
pip install -r requirements.txt

# 4. Create .env file with database URL
echo DATABASE_URL=postgresql://... > .env

# 5. Run migrations
prisma migrate dev

# 6. Start server
uvicorn app.main:app --reload --port 8000
```

### Verify Setup

```bash
curl http://127.0.0.1:8000/health
# Expected: {"status": "ok", "version": "1.0.0", ...}
```

---

## API Endpoints

### 1. Health Check

**GET** `/health`

Returns server and database status.

**Response (200 OK):**

```json
{
  "status": "ok",
  "version": "1.0.0",
  "app_name": "PurseAgent AI",
  "environment": "development",
  "database": "connected",
  "tasks": ["A", "B"]
}
```

**Response (503 Service Unavailable):**

```json
{
  "detail": "Database connection failed"
}
```

---

### 2. Simulate Review (Task A)

**POST** `/api/v1/simulate-review`

Generate a realistic review and rating for a product based on a user persona.

**Request Body:**

```json
{
  "user_persona": {
    "user_id": "user123",
    "name": "Alice Johnson",
    "budget": 50,
    "preferences": ["quality", "eco-friendly"],
    "price_sensitivity": "medium",
    "review_style": "detailed"
  },
  "product": {
    "product_id": "prod_456",
    "name": "Leather Wallet",
    "category": "fashion",
    "brand": "LuxeBrand",
    "price": 45.99,
    "description": "Premium leather wallet with RFID protection"
  }
}
```

**Response (200 OK):**

```json
{
  "predicted_rating": 4.5,
  "simulated_review": "Excellent quality wallet! The leather feels premium and the RFID protection is a nice touch...",
  "confidence": 0.92,
  "reasoning": "User values quality and eco-friendly products. Product aligns with budget and preferences."
}
```

**Response (504 Gateway Timeout):**

```json
{
  "detail": "Agent took too long to respond (timeout)"
}
```

**Response (500 Internal Server Error):**

```json
{
  "detail": "Agent error: <error message>"
}
```

---

### 3. Get Recommendations (Task B)

**POST** `/api/v1/recommend`

Get personalized product recommendations for a user.

**Request Body:**

```json
{
  "user_persona": {
    "user_id": "user123",
    "name": "Alice Johnson",
    "budget": 50,
    "preferences": ["quality", "eco-friendly"],
    "purchase_history": ["prod_100", "prod_101"]
  },
  "top_k": 5,
  "domain": "fashion"
}
```

**Valid Domains:**

- `fashion` — Apparel, accessories, footwear
- `electronics` — Gadgets, tech devices
- `books` — Physical and digital books
- `food` — Grocery, specialty foods

**Response (200 OK):**

```json
{
  "recommendations": [
    {
      "rank": 1,
      "product_id": "prod_789",
      "name": "Premium Organic Cotton T-Shirt",
      "category": "fashion",
      "score": 0.95,
      "reason": "Matches eco-friendly preference and budget"
    },
    {
      "rank": 2,
      "product_id": "prod_790",
      "name": "Sustainable Bamboo Wallet",
      "category": "fashion",
      "score": 0.88,
      "reason": "High quality, eco-friendly material"
    }
  ],
  "is_cold_start": false,
  "total": 2
}
```

**Response (422 Unprocessable Entity):**

```json
{
  "detail": "Domain must be one of: fashion, electronics, books, food"
}
```

**Response (504 Gateway Timeout):**

```json
{
  "detail": "Agent took too long to respond (timeout)"
}
```

---

## Request/Response Models

### User Persona (Request)

```python
{
  "user_id": str,           # Unique user identifier
  "name": str,              # User's name (optional)
  "budget": float,          # Maximum spending amount
  "preferences": list[str], # Product preferences/interests
  "price_sensitivity": str, # "low", "medium", "high" (optional)
  "review_style": str,      # Review tone preference (optional)
  "purchase_history": list[str]  # Previous product IDs (optional)
}
```

### Product (Request)

```python
{
  "product_id": str,    # Unique product identifier
  "name": str,          # Product name
  "category": str,      # Product category
  "brand": str,         # Brand name (optional)
  "price": float,       # Product price
  "description": str    # Product description (optional)
}
```

### SimulateReviewResponse

```python
{
  "predicted_rating": float,    # 1.0 to 5.0
  "simulated_review": str,      # Generated review text
  "confidence": float,           # 0.0 to 1.0 confidence score
  "reasoning": str              # Why this review was generated
}
```

### RecommendationItem

```python
{
  "rank": int,         # Position in recommendation list
  "product_id": str,   # Unique product identifier
  "name": str,         # Product name
  "category": str,     # Product category
  "score": float,      # 0.0 to 1.0 recommendation score
  "reason": str        # Why this product was recommended
}
```

### RecommendResponse

```python
{
  "recommendations": list[RecommendationItem],
  "is_cold_start": bool,  # True if user has no history
  "total": int            # Number of recommendations
}
```

---

## Error Handling

### HTTP Status Codes

| Code | Meaning             | Example                        |
| ---- | ------------------- | ------------------------------ |
| 200  | Success             | Both endpoints return data     |
| 422  | Validation Error    | Invalid domain in `/recommend` |
| 500  | Server Error        | Agent runtime error            |
| 503  | Service Unavailable | Database connection failed     |
| 504  | Gateway Timeout     | Agent execution exceeded 60s   |

### Error Response Format

All errors follow this format:

```json
{
  "detail": "Human-readable error message"
}
```

### Timeout Behavior

- **Default Timeout:** 60 seconds per request
- **What Happens:** If agent doesn't respond within 60s, request returns 504
- **Why:** Prevents hanging connections and resource exhaustion

---

## Database Schema

### User Table

```sql
CREATE TABLE "User" (
  id              String    @id @default(cuid())
  user_id         String    @unique
  persona         Json      -- Stores user preferences
  created_at      DateTime  @default(now())
  updated_at      DateTime  @updatedAt
)
```

### Simulation Table

```sql
CREATE TABLE "Simulation" (
  id              String    @id @default(cuid())
  user_id         String
  product         Json      -- Product details
  result          Json      -- Generated review + rating
  confidence      Float
  created_at      DateTime  @default(now())

  @@index([user_id])
}
```

### Recommendation Table

```sql
CREATE TABLE "Recommendation" (
  id              String    @id @default(cuid())
  user_id         String
  recommendations Json      -- List of recommended items
  domain          String    -- Category (fashion, etc)
  is_cold_start   Boolean
  created_at      DateTime  @default(now())

  @@index([user_id, domain])
}
```

### AuditLog Table

```sql
CREATE TABLE "AuditLog" (
  id              String    @id @default(cuid())
  endpoint        String    -- API path
  method          String    -- HTTP method
  status_code     Int       -- Response code
  duration_ms     Int       -- Request duration
  error_msg       String?   -- Error message (if failed)
  created_at      DateTime  @default(now())
}
```

---

## Authentication (Future)

**Note:** Currently no authentication is implemented. For production:

- [ ] Add JWT token validation
- [ ] Implement API key system
- [ ] Add rate limiting per user
- [ ] Log user IP addresses
- [ ] Implement CORS whitelist for frontend domain

---

## Development Notes

### Local Testing

Use Swagger UI to test endpoints interactively:

```
http://127.0.0.1:8000/docs
```

### Example cURL Commands

**Test Health:**

```bash
curl http://127.0.0.1:8000/health
```

**Test Simulate Review:**

```bash
curl -X POST http://127.0.0.1:8000/api/v1/simulate-review \
  -H "Content-Type: application/json" \
  -d '{
    "user_persona": {"user_id": "user1", "budget": 50, "preferences": ["quality"]},
    "product": {"product_id": "prod1", "name": "Wallet", "price": 45.99}
  }'
```

**Test Recommend:**

```bash
curl -X POST http://127.0.0.1:8000/api/v1/recommend \
  -H "Content-Type: application/json" \
  -d '{
    "user_persona": {"user_id": "user1", "budget": 50},
    "top_k": 5,
    "domain": "fashion"
  }'
```

---

## Support & Questions

For issues or questions:

1. Check error logs in terminal
2. Review audit logs in database: `SELECT * FROM "AuditLog" ORDER BY created_at DESC`
3. Check `/docs` Swagger UI for request validation errors
4. Verify `.env` file has correct `DATABASE_URL`
