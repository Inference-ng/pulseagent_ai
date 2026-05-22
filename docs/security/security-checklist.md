# Security Checklist — PurseAgent AI

> Owner: [4th Team Member]
> Review with Nwokedi before submission

## API Security
- [ ] No API keys in source code or committed `.env` files
- [ ] `.env` is in `.gitignore` — verify with `git status` before pushing
- [ ] All endpoints have input validation (Pydantic models reject bad input)
- [ ] CORS restricted to `http://localhost:3000` only (not `*`)
- [ ] Rate limiting: max 10 requests/min per IP on AI endpoints

## Prompt Injection Protection
- [ ] User-provided `context` strings are sanitized before LLM input
- [ ] Product descriptions are truncated to max 500 chars before sending to LLM
- [ ] No raw user input passed directly as system prompts

## Container Security
- [ ] Docker containers run as non-root user (add `USER nobody` in Dockerfile)
- [ ] No secrets in Dockerfile (use env vars, not COPY .env)
- [ ] `requirements.txt` has pinned versions — no `>=` wildcards

## Data Privacy
- [ ] No real user PII stored in the database
- [ ] Demo personas use fictional names only
- [ ] Logs do not contain API keys or user review content

## Submission Security
- [ ] Final GitHub repo is PUBLIC (required for submission)
- [ ] Double-check: `git log --all -- .env` shows no .env commits
- [ ] Solution paper does not contain any API keys or credentials
