# 📋 Team Task Assignments

Welcome to the **PurseAgent AI** project. Instead of searching through every folder, refer to this document for your specific responsibilities.

---

### 🧠 AI Agent — Emmanuel's Domain
> **Elebiemayo Iseoluwa Emmanuel** | LangChain/LangGraph Agent Core
**Working Directory:** `apps/ai-agent/`

**Tasks:**
- [ ] Read the setup instructions in `apps/ai-agent/README.md`
- [ ] Set up LangChain/LangGraph logic
- [ ] Implement Task A (User Modeling & Review Simulation)
- [ ] Implement Task B (Product Recommendations via Retrieval/FAISS)
- [ ] Connect the agent to the provided LLM models (Llama 3 / GPT)

---

### ⚡ Backend API — Nwokedi's Domain
> **Nwokedi Ikechukwu** | FastAPI Backend + Docker Infrastructure
**Working Directory:** `apps/backend/` and `infra/`

**Tasks:**
- [ ] Read the setup instructions in `apps/backend/README.md`
- [ ] Set up the FastAPI project structure and PostgreSQL connection
- [ ] Create `POST /api/v1/simulate-review` endpoint (Connecting to Emmanuel's AI logic)
- [ ] Create `POST /api/v1/recommend` endpoint
- [ ] Ensure the main `docker-compose.yml` successfully spins up all services

---

### 🎨 Frontend Dashboard — Victor's Domain
> **Victor Chukwuebuka** | React Demo Dashboard
**Working Directory:** `apps/frontend/`

**Tasks:**
- [ ] Read the setup instructions in `apps/frontend/README.md`
- [ ] Initialize the React / Vite app with TailwindCSS
- [ ] Build the UI for the "Simulate Review" input form and response display
- [ ] Build the UI for the "Product Recommendations" view
- [ ] Integrate with Nwokedi's FastAPI backend endpoints

---

### 📄 Docs & Pitch — David's Domain
> **David Aborowa** | Solution Paper · Pitch Deck · Security · Submission
**Working Directory:** `docs/`

**Tasks:**
- [ ] Read the instructions in `docs/README.md`
- [ ] Complete the Solution Paper (`docs/solution-paper/solution-paper.md`)
- [ ] Complete the Security Checklist (`docs/security/security-checklist.md`)
- [ ] Create the Pitch Deck presentation slides
- [ ] Submit the final GitHub repository link, Pitch Deck, and Solution paper to the Hackathon submission portal
