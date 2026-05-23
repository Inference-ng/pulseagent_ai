# 📄 Docs & Pitch — 4th Team Member's Domain
> **[DAVID ABOROWA]** | Solution Paper · Pitch Deck · Security · Submission

---

## Your Mission
You are the team's **primary contact with the judges**. The solution paper is the **first thing judges read** — the brief says it outright. A weak paper = lost points regardless of how good the code is. You also own the pitch deck for the Data & AI Summit if we are shortlisted.

---

## Your Deliverables

1. **Solution Paper** (4–8 pages PDF) — due 24 May, end of day
2. **Architecture Diagram** (for the paper + pitch deck)
3. **Pitch Deck** (for Data & AI Summit, 29 May–1 June if shortlisted)
4. **Security Review** — API safety checklist
5. **Submission** — submit all 3 deliverables via the form

---

## Directory Structure

```
docs/
├── solution-paper/
│   ├── solution-paper.md         # Write here → export as PDF
│   ├── solution-paper.pdf        # Final submission PDF
│   └── figures/
│       ├── architecture.png       # System architecture diagram
│       ├── task-a-flow.png        # Task A agent flow
│       └── task-b-flow.png        # Task B agent flow
├── pitch-deck/
│   ├── pulseagent-pitch.pptx     # PowerPoint pitch deck
│   └── pulseagent-pitch.pdf      # PDF export
├── security/
│   └── security-checklist.md     # Security review notes
└── README.md
```

---

## Solution Paper — Structure (4–8 Pages)

Use this exact structure. Judges read this against the 100-point rubric.

---

### Page 1: Title + Abstract
```
Title: PulseAgent AI: A Dual-Task LLM Agent for User Modeling 
       and Personalized Recommendation on Nigerian E-Commerce Platforms

Team: [Names, Institutions]
Date: May 2026

Abstract (150 words):
- What problem does it solve
- What we built (Task A + Task B)
- Key approach (LangGraph agents, FAISS, Nigerian context)
- Key results (ROUGE score, NDCG@10 if available)
```

### Page 2: Problem Statement & Motivation
- Most businesses treat all users the same → generic, irrelevant experiences
- Nigerian e-commerce context: price sensitivity, naira fluctuations, delivery friction
- Why existing systems fail: no behavioral memory, no contextual reasoning
- Our contribution: an agent that remembers, reasons, and recommends

### Page 3: System Architecture
- Include the architecture diagram (ask Victor/Nwokedi for it)
- Describe the two-agent system:
  - **User Modeling Agent** (LangGraph + FAISS memory + LLM)
  - **Recommendation Agent** (LangGraph + FAISS retrieval + re-ranking)
- Describe the data pipeline: Amazon Reviews → preprocessing → FAISS index

### Page 4: Task A — User Modeling Approach
- How user personas are constructed from behavioral history
- LangGraph state machine: retrieve → contextualize → generate
- Nigerian tone injection: how we added cultural context (bonus marks)
- Prompt engineering strategy for review generation
- How we calibrate ratings (anchor to user's historical average)
- Metrics: ROUGE-L, BERTScore, RMSE

### Page 5: Task B — Recommendation Approach
- Item embedding strategy (Sentence Transformers + FAISS)
- Ranking pipeline: retrieval → scoring → LLM re-ranking with reasoning
- Cold-start strategy (explain the 3-step fallback)
- Cross-domain recommendation logic
- Metrics: NDCG@10, Hit Rate@10

### Page 6: Experiments & Results
- Dataset statistics (# users, # items, # reviews)
- Baseline comparison (simple collaborative filtering vs our agent)
- Ablation: with/without Nigerian context layer
- Ablation: with/without FAISS memory (cold-start performance)
- Table format preferred

### Page 7: Limitations & Future Work
- Current limitations (dataset size, latency, LLM cost)
- What we'd do with 3 more months:
  - Fine-tune an LLM on Nigerian e-commerce data
  - Real-time behavioral tracking
  - A/B testing framework for businesses

### Page 8: References
- Amazon Reviews 2023 dataset paper
- LangChain / LangGraph documentation
- FAISS paper (Johnson et al., 2019)
- Relevant recommendation system papers

---

## Architecture Diagram — What to Draw

Use **draw.io** (free at app.diagrams.net) or **Canva**:

```
[User / Judge] 
     ↓  HTTP
[React Dashboard]
     ↓  API calls
[FastAPI Backend]
     ↓  Python calls
     ├──→ [User Modeling Agent (LangGraph)]
     │         ↓ retrieves from
     │    [FAISS User Memory Store]
     │         ↓ calls
     │    [LLM (Llama 3 / GPT-4o-mini)]
     │
     └──→ [Recommendation Agent (LangGraph)]
               ↓ retrieves from
          [FAISS Item Index]
               ↓ calls
          [LLM (Llama 3 / GPT-4o-mini)]

[Datasets: Amazon Reviews | Yelp | Goodreads]
     → preprocessed → [FAISS Indexes]
```

---

## Security Checklist

Work with Nwokedi to verify these before submission:

- [ ] No API keys committed to GitHub (check `.gitignore` includes `.env`)
- [ ] Input validation on all API endpoints (prevent prompt injection)
- [ ] Rate limiting on `/api/v1/simulate-review` and `/api/v1/recommend`
- [ ] CORS restricted to frontend origin only
- [ ] No sensitive user data stored in plaintext
- [ ] Docker containers run as non-root user
- [ ] `requirements.txt` has pinned versions (no `latest`)

---

## Pitch Deck Structure (If Shortlisted for Summit)

10 slides, max 20 minutes:

| Slide | Content |
|---|---|
| 1 | Title + Team |
| 2 | The Problem (generic experiences cost businesses money) |
| 3 | The Solution (PulseAgent AI demo gif) |
| 4 | How It Works (architecture — keep it simple) |
| 5 | Live Demo (show the dashboard) |
| 6 | Task A Results (review quality, RMSE) |
| 7 | Task B Results (NDCG@10, cold-start) |
| 8 | Nigerian Context (the bonus — speak their language) |
| 9 | Business Model (₦20k–₦100k/mo SaaS, API calls) |
| 10 | Team + Ask / Next Steps |

**Design tips:**
- Use team's brand colours: emerald green + amber
- Dark slide background
- Screenshots of the live dashboard
- One key stat per slide

---

## Submission Checklist (You Own This)

Before midnight, 24 May 2026:

- [ ] Solution paper PDF (4–8 pages) ready
- [ ] GitHub repo URL confirmed: `https://github.com/pulseagent-bct/pulseagent-ai`
- [ ] Deployed agent URL (get from Nwokedi — could be Railway/Render/localhost)
- [ ] All three submitted via BCT submission form
- [ ] Confirmation email received and forwarded to team WhatsApp

---

## Tools Recommended
- **Paper writing**: Google Docs → export PDF
- **Diagrams**: [app.diagrams.net](https://app.diagrams.net) (free draw.io)
- **Pitch deck**: Canva (free), PowerPoint, or Google Slides
- **Grammar check**: Grammarly

---

## Git Workflow
```bash
git checkout -b feat/docs
# Work in docs/
git add docs/
git commit -m "docs: add solution paper draft and architecture diagram"
git push origin feat/docs
# Open PR to main when ready
```
