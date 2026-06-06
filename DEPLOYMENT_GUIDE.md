# PRETO — Deployment Guide

**Live URL**: https://preto.onrender.com  
**GitHub**: https://github.com/Howardstark0701/PRETO  
**Deployed**: June 7, 2026  
**Author**: TANGO

---

## Overview

PRETO is deployed as a single web service on Render (free tier).  
The backend (FastAPI) and frontend (React) are served from one container — no separate frontend hosting needed.

---

## Architecture in Production

```
Browser → https://preto.onrender.com
              │
              ├── /api/*          → FastAPI (Python)
              ├── /assets/*       → React static files (JS/CSS)
              └── /*              → index.html (SPA catch-all)
```

The React `dist/` is built during deployment and served directly by FastAPI via `StaticFiles`.

---

## Files That Handle Deployment

| File | Purpose |
|------|---------|
| `Dockerfile` | Multi-stage build (Node → Python → production image) |
| `render.yaml` | Render deployment config (auto-deploy, env vars) |
| `requirements.txt` | Pinned Python dependencies |
| `.python-version` | Pins Python 3.11.9 for Render |
| `.github/workflows/ci.yml` | CI pipeline (tests, frontend build, Docker smoke test) |
| `.env.example` | Template for all required environment variables |

---

## How the Dockerfile Works

```
Stage 1 — Frontend Build (Node 20 Alpine)
  - npm ci
  - npm run build → produces frontend/dist/

Stage 2 — Python Dependencies (Python 3.10 slim)
  - pip install -r requirements.txt

Stage 3 — Production Image (Python 3.10 slim)
  - Copies Python packages from Stage 2
  - Copies app source code
  - Copies frontend/dist/ from Stage 1
  - Runs as non-root user (preto)
  - Exposes port 8000
  - CMD: python main.py
```

---

## How main.py Serves the Frontend

```python
# Serves /assets/* (JS, CSS, images)
app.mount("/assets", StaticFiles(directory="frontend/dist/assets"))

# Catch-all: any non-API route returns index.html
@app.get("/{full_path:path}")
async def serve_spa(full_path: str):
    return FileResponse("frontend/dist/index.html")
```

This means hitting `/`, `/graph`, `/analytics` etc. all return the React app.  
Only `/api/*` routes are handled by FastAPI endpoints.

---

## Deploying to Render (First Time)

### Step 1 — Push code to GitHub
```bash
git remote add origin https://github.com/YOUR_USERNAME/PRETO.git
git push -u origin master
```

### Step 2 — Create Web Service on Render
1. Go to https://render.com → New → Web Service
2. Connect your GitHub repo
3. Render auto-detects `render.yaml` — or configure manually:
   - **Runtime**: Python 3
   - **Build Command**: `pip install -r requirements.txt && npm install --prefix frontend && npm run build --prefix frontend`
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`

### Step 3 — Add Environment Variables
Add these in Render dashboard → Environment:

| Variable | Value |
|----------|-------|
| `GITHUB_TOKEN` | Your GitHub PAT |
| `GITHUB_CLIENT_ID` | From GitHub OAuth App |
| `GITHUB_CLIENT_SECRET` | From GitHub OAuth App |
| `GITHUB_REDIRECT_URI` | `https://YOUR-APP.onrender.com/api/auth/github/callback` |
| `FRONTEND_URL` | `https://YOUR-APP.onrender.com` |
| `NIM_API_KEY` | From https://build.nvidia.com |
| `NIM_API_URL` | `https://integrate.api.nvidia.com/v1` |
| `NIM_MODEL` | `meta/llama-3.1-70b-instruct` |
| `MAX_REQUESTS_PER_MINUTE` | `40` |
| `SECRET_KEY` | Click **Generate** in Render |
| `API_HOST` | `0.0.0.0` |
| `API_PORT` | `8000` |
| `DEBUG_MODE` | `false` |

### Step 4 — Deploy
Click **Deploy Web Service** and watch the logs.  
First deploy takes ~3-5 minutes (installing deps + building frontend).

---

## Redeploying After Changes

Every push to `master` triggers an auto-deploy on Render.

```bash
git add .
git commit -m "Your changes"
git push
```

Render picks it up automatically. No manual action needed.

To force a redeploy: **Manual Deploy → Clear build cache & deploy**

---

## Issues We Hit + Fixes

### Issue 1: GitHub Push Protection blocked the push
**Cause**: Real `GITHUB_TOKEN` was hardcoded in `NEXT_STEPS_NIM.md` and present in old commits.  
**Fix**:
1. Replaced token in the file with placeholder
2. Used `git-filter-repo` to rewrite history and scrub the token:
```bash
echo "github_pat_REAL_TOKEN==>github_pat_REDACTED" > replacements.txt
python -m git_filter_repo --replace-text replacements.txt --force
rm replacements.txt
git remote add origin https://github.com/Howardstark0701/PRETO.git
git push -u origin master --force
```
3. Revoked the old token on GitHub → Settings → Tokens

**Lesson**: Never commit `.env` files. Always check `.gitignore` includes `.env`.

---

### Issue 2: pydantic-core build failed (Rust not available)
**Cause**: Render's build environment uses Python 3.14 by default, which requires pydantic-core to compile from source (needs Rust). Render's free tier has a read-only filesystem so Cargo fails.  
**Fix**: Added `.python-version` file to pin Python 3.11.9 where pre-built pydantic v2 wheels are available:
```
3.11.9
```
This lets pip download pre-compiled wheels instead of building from source.

---

### Issue 3: `npm` not found in PowerShell
**Cause**: Node.js was installed but not on PowerShell's PATH (only on Git Bash PATH).  
**Fix**: Always run npm commands in Git Bash:
```bash
cd /c/Users/patha/PRETO/frontend
npm run build
```

---

### Issue 4: `git-filter-repo` not found as git command
**Cause**: Installed via pip to user site-packages, not accessible as a git subcommand.  
**Fix**: Run via Python module instead:
```bash
python -m git_filter_repo --replace-text replacements.txt --force
```

---

## Running Locally

### Backend
```bash
# Activate virtual environment
source venv/Scripts/activate   # Git Bash
# or
venv\Scripts\Activate.ps1      # PowerShell

# Start server
python main.py
# API at http://localhost:8000
# Docs at http://localhost:8000/api/docs
```

### Frontend (development)
```bash
cd frontend
npm run dev
# UI at http://localhost:5173
```

### Frontend (production build)
```bash
cd frontend
npm run build
# Output in frontend/dist/
# Served by FastAPI at http://localhost:8000
```

---

## Running with Docker

### Development
```bash
docker-compose up --build
# App at http://localhost:8000
```

### Production (with Nginx + PostgreSQL + Redis)
```bash
docker-compose -f docker-compose.prod.yml up --build
```

---

## CI/CD Pipeline

`.github/workflows/ci.yml` runs on every push to `master`:

| Job | What it does |
|-----|-------------|
| `backend` | Installs deps, runs linter, runs pytest |
| `frontend` | npm ci, npm run build, uploads dist artifact |
| `docker` | Builds Docker image, smoke tests `/api/health` |
| `security` | Runs `safety check` on requirements.txt |

---

## Health Check

Once deployed, verify everything is working:

```bash
# Health endpoint
curl https://preto.onrender.com/api/health

# Expected response:
{
  "status": "healthy",
  "message": "PRETO API is running",
  "version": "0.2.0"
}
```

```bash
# NIM AI health
curl https://preto.onrender.com/api/insights/health

# Expected:
{
  "status": "healthy",
  "insights_service": "NVIDIA NIM",
  "nim_configured": true
}
```

---

## Important Notes

- **Free tier spins down after 15 min inactivity** — first request after idle takes ~50 seconds to wake up. Upgrade to paid tier to avoid this.
- **SQLite in production** — data resets on every deploy (ephemeral filesystem). For persistent data, switch to PostgreSQL (use `docker-compose.prod.yml` as reference).
- **GitHub OAuth callback URL** must match exactly what's set in your GitHub OAuth App settings.
- **Revoke any token** that was ever committed to git history — treat it as compromised regardless of history rewrites.

---

## Quick Reference

| Thing | Value |
|-------|-------|
| Live URL | https://preto.onrender.com |
| API Docs | https://preto.onrender.com/api/docs |
| Health | https://preto.onrender.com/api/health |
| GitHub | https://github.com/Howardstark0701/PRETO |
| Render Dashboard | https://dashboard.render.com |
| NVIDIA NIM | https://build.nvidia.com |
| GitHub Tokens | https://github.com/settings/tokens |
| GitHub OAuth Apps | https://github.com/settings/developers |

---

**Last Updated**: June 7, 2026  
**Status**: 🟢 Live and running
