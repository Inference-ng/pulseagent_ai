# Backend Setup Guide

**Target:** Get the FastAPI backend running locally in 5 minutes.

---

## Prerequisites

### System Requirements

- **Python:** 3.12+ (check with `python --version`)
- **Node.js:** 18+ (for development tools, optional)
- **Git:** Latest version

### Accounts Required

- **Neon PostgreSQL:** Free account at https://console.neon.tech
  - Get your connection string: `postgresql://user:password@host/database`

---

## Step 1: Get Neon Connection String

1. Go to https://console.neon.tech
2. Create a project or use existing one
3. Copy the connection string (looks like):
   ```
   postgresql://neonuser:xxxxx@ep-young-bird-aq69b05v-pooler.c-8.us-east-1.aws.neon.tech/neondb?sslmode=require
   ```
4. Save it — you'll need it in Step 3

---

## Step 2: Clone & Navigate

```bash
# Clone the repo
git clone https://github.com/your-org/pulseagent_ai.git
cd pulseagent_ai

# Navigate to backend
cd apps/backend
```

---

## Step 3: Create Environment File

Create `.env` in `apps/backend/`:

```bash
# Option A: Create with echo (Windows PowerShell)
"DATABASE_URL=postgresql://neonuser:xxxxx@ep-young-bird-aq69b05v-pooler.c-8.us-east-1.aws.neon.tech/neondb?sslmode=require" | Out-File -Encoding UTF8 .env

# Option B: Create with text editor
# Open .env and paste:
DATABASE_URL=postgresql://neonuser:xxxxx@...
```

**⚠️ Important:** Never commit `.env` to Git. It's already in `.gitignore`.

---

## Step 4: Set Up Virtual Environment

```bash
# Create venv
python -m venv venv

# Activate venv (Windows)
.\venv\Scripts\activate

# Activate venv (macOS/Linux)
source venv/bin/activate

# Verify activation (should show "venv" prefix)
```

---

## Step 5: Install Dependencies

```bash
# Upgrade pip first
python -m pip install --upgrade pip setuptools wheel

# Install all dependencies
pip install -r requirements.txt
```

**Expected output:** `Successfully installed 34 packages`

---

## Step 6: Initialize Database

```bash
# Generate Prisma client
prisma generate

# Run migrations to Neon
prisma migrate dev --name init
```

**Expected output:**

```
✔ Database created
✔ Migration applied successfully
```

**What this does:**

- Creates 4 tables: User, Simulation, Recommendation, AuditLog
- Creates indexes for performance
- Generates Prisma Python client

---

## Step 7: Start the Server

```bash
# Make sure venv is activated
uvicorn app.main:app --reload --port 8000
```

**Expected output:**

```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Press CTRL+C to quit
INFO:     Application startup complete
```

---

## Step 8: Verify It Works

### Option A: Open Browser

```
http://127.0.0.1:8000/docs
```

You should see the interactive Swagger UI with all endpoints.

### Option B: Test via Terminal

```bash
# Test health check
curl http://127.0.0.1:8000/health

# Expected response:
{
  "status": "ok",
  "version": "1.0.0",
  "app_name": "PulseAgent AI",
  "environment": "development",
  "database": "connected",
  "tasks": ["A", "B"]
}
```

---

## Troubleshooting

### Issue: "ModuleNotFoundError: No module named 'fastapi'"

**Solution:** Make sure venv is activated

```bash
.\venv\Scripts\activate  # Windows
source venv/bin/activate  # macOS/Linux
```

### Issue: "UnicodeEncodeError" on Windows

**Solution:** Already fixed. Just run migrations fresh:

```bash
prisma migrate reset
```

### Issue: "Connection refused" to database

**Reasons:**

1. Wrong connection string in `.env`
2. Neon project is sleeping (restart it)
3. Network/firewall issue

**Solution:**

```bash
# Verify connection string is correct
cat .env

# Test database connectivity
python -c "import asyncio; from app.database import connect_db; asyncio.run(connect_db())"
```

### Issue: "relation 'User' does not exist"

**Solution:** Migrations didn't run. Try:

```bash
prisma migrate dev --name init
```

### Issue: Port 8000 already in use

**Solution:** Use different port

```bash
uvicorn app.main:app --reload --port 8001
```

---

## Development Workflow

### Running the Server

```bash
# In venv
uvicorn app.main:app --reload --port 8000
```

### Making Changes

- Modify files in `app/`
- Server auto-reloads (thanks to `--reload`)
- Test in Swagger UI: http://127.0.0.1:8000/docs

### Database Schema Changes

```bash
# Edit prisma/schema.prisma
# Then run:
prisma migrate dev --name description_of_change
```

### Viewing Data

```bash
# Open Prisma Studio (GUI for database)
prisma studio
```

---

## Testing Endpoints Manually

### Using Swagger UI (Easiest)

1. Go to http://127.0.0.1:8000/docs
2. Click on an endpoint
3. Click "Try it out"
4. Modify request body
5. Click "Execute"

### Using cURL

**Health Check:**

```bash
curl http://127.0.0.1:8000/health
```

**Simulate Review (Task A):**

```bash
curl -X POST http://127.0.0.1:8000/api/v1/simulate-review \
  -H "Content-Type: application/json" \
  -d '{
    "user_persona": {
      "user_id": "user123",
      "budget": 50,
      "preferences": ["quality"]
    },
    "product": {
      "product_id": "prod456",
      "name": "Leather Wallet",
      "category": "fashion",
      "price": 45.99
    }
  }'
```

**Get Recommendations (Task B):**

```bash
curl -X POST http://127.0.0.1:8000/api/v1/recommend \
  -H "Content-Type: application/json" \
  -d '{
    "user_persona": {
      "user_id": "user123",
      "budget": 100
    },
    "top_k": 5,
    "domain": "fashion"
  }'
```

---

## Docker Setup (Optional)

### Build Container

```bash
docker build -t pulseagent-backend .
```

### Run Container

```bash
docker run \
  -e DATABASE_URL="postgresql://..." \
  -p 8000:8000 \
  pulseagent-backend
```

---

## Environment Variables

Create `.env` with these variables:

```env
# Required
DATABASE_URL=postgresql://user:password@host/database

# Optional (defaults provided)
ENVIRONMENT=development
APP_NAME=PulseAgent AI
APP_VERSION=1.0.0
CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
```

---

## Common Commands Cheat Sheet

```bash
# Activate venv
.\venv\Scripts\activate

# Install packages
pip install -r requirements.txt

# Update Prisma client
prisma generate

# Run migrations
prisma migrate dev

# Reset database (careful!)
prisma migrate reset

# View database in GUI
prisma studio

# Start server
uvicorn app.main:app --reload

# Stop server
Ctrl+C

# Run tests (future)
pytest

# Check for linting issues
flake8 app/
```

---

## What's Next?

1. ✅ Server running locally
2. ✅ Swagger UI at /docs
3. ✅ Database connected to Neon
4. ⏳ Waiting for AI agents to be ready (Emmanuel/Iseoluwa)
5. ⏳ Then: Implement integration tests
6. ⏳ Finally: Deploy to production

---

## Getting Help

### Check Logs

```bash
# Terminal where server is running shows real-time logs
# Look for ERROR or WARNING lines
```

### View Database

```bash
# Open Prisma Studio
prisma studio
# Opens GUI at http://localhost:5555
```

### Check Configuration

```bash
# Verify all settings loaded correctly
cat .env
echo $DATABASE_URL
```

### Verify Python Version

```bash
python --version  # Should be 3.12+
```

---

## Production Checklist

Before deploying:

- [ ] Database: Neon project created & backed up
- [ ] Secrets: `.env` file NOT in git
- [ ] Tests: All passing (Phase 7)
- [ ] Monitoring: Logs configured
- [ ] CORS: Frontend domain added
- [ ] Rate limiting: Configured (future)
- [ ] Documentation: Reviewed

---

**You're all set! 🚀 Start the server and test endpoints in Swagger UI.**
