# PRETO — Session Progress & Roadmap

**Last Updated:** June 7, 2026  
**Backend Version:** 0.2.0 (36+ endpoints, FastAPI, SQLite)

---

## ✅ DONE — All Sessions

### Backend
- FastAPI app, 34+ endpoints across 5 routers
- SQLite DB (5 tables + github OAuth fields added)
- In-memory caching, background scheduler, CRUD layer
- Auth: register, login, JWT, refresh tokens, API keys
- NVIDIA NIM AI integration (insights, user analysis, NL queries)
- Advanced features: export, analytics, recommendations, compare
- GitHub scraper (async, pagination, rate-limit aware)

### Frontend (Session 1)
- React + Vite, Palantir dark theme
- 6 pages: Search, User Intel, AI Insights, Analytics, System, Auth
- All 34 backend endpoints wired in `api.js`

### GitHub OAuth + Graph (Session 2 — this session)
- `app/api/github_oauth.py` — full OAuth2 flow, no extra deps
  - `GET /api/auth/github` — redirects to GitHub
  - `GET /api/auth/github/callback` — exchanges code, creates user, returns JWT
  - `GET /api/auth/github/status` — config check
- `app/models/auth.py` — User model updated with `github_id`, `github_login`, `github_token`, `avatar_url`
- `main.py` — `github_oauth_router` registered
- `.env` — added `GITHUB_CLIENT_ID`, `GITHUB_CLIENT_SECRET`, `FRONTEND_URL` vars
- `frontend/src/pages/AuthPage.jsx` — "Continue with GitHub" button, avatar display, OAuth callback handler
- `frontend/src/pages/GraphPage.jsx` — D3 v7 force-directed graph (lazy CDN load)
  - User → Repo → Language nodes
  - Drag, zoom, click-for-details panel
  - Star badges on repo nodes
- `frontend/src/App.jsx` — Graph page added to sidebar + routing

---

## 🔧 TO ACTIVATE GitHub OAuth (2 min setup)

1. Go to https://github.com/settings/developers → "New OAuth App"
2. Fill in:
   - Homepage URL: `http://localhost:5173`
   - Callback URL: `http://localhost:8000/api/auth/github/callback`
3. Copy Client ID + Client Secret
4. Add to `.env`:
   ```
   GITHUB_CLIENT_ID=your_client_id_here
   GITHUB_CLIENT_SECRET=your_client_secret_here
   ```
5. Restart backend (`python main.py`)
6. Click "Continue with GitHub" on Auth page

---

## 🚀 To Run

```
# Terminal 1 — backend
python main.py

# Terminal 2 — frontend (add nodejs to PATH first)
$env:PATH = "C:\Program Files\nodejs;" + $env:PATH
cd C:\Users\patha\PRETO\frontend
& "C:\Program Files\nodejs\node.exe" "C:\Program Files\nodejs\node_modules\npm\bin\npm-cli.js" run dev
```
Open: http://localhost:5173

---

## 📋 REMAINING (Session 3 — Future)

- **PDF export** — backend: `pip install reportlab`, add `/api/advanced/export/pdf` endpoint, wire to frontend Analytics export button
- **Contributor graph expansion** — fetch contributors via GitHub API, add `contributor` node type to GraphPage
- **Graph search** — filter nodes by language/stars within the graph view
- **Multi-user compare** — load two users side-by-side in the graph

### Left-out (later addons as planned)
- Option A: PostgreSQL migration, Redis, Docker prod
- Option D: Full test suite, load testing, Pydantic v2 fixes

---

## 🏗️ Full Project Structure

```
PRETO/
├── main.py
├── .env                         ← add GITHUB_CLIENT_ID/SECRET here
├── app/
│   ├── api/
│   │   ├── routes.py            # Repo endpoints
│   │   ├── auth_routes.py       # Auth endpoints
│   │   ├── github_oauth.py      # ← NEW GitHub OAuth
│   │   ├── insights_routes.py   # NIM AI
│   │   ├── advanced_routes.py   # Export/analytics
│   │   ├── auth.py              # JWT + rate limiting
│   │   ├── insights.py          # NIM client
│   │   ├── cache.py / crud.py / sync.py / scheduler.py
│   ├── models/
│   │   ├── auth.py              # ← UPDATED: github_id/token/avatar fields
│   │   └── database.py
│   └── scrapers/github_scraper.py
├── frontend/
│   ├── src/
│   │   ├── api.js               # All endpoints incl. github OAuth
│   │   ├── App.jsx              # ← UPDATED: Graph in sidebar
│   │   ├── App.css / index.css
│   │   ├── pages/
│   │   │   ├── SearchPage.jsx
│   │   │   ├── UserPage.jsx
│   │   │   ├── GraphPage.jsx    # ← NEW D3 force graph
│   │   │   ├── InsightsPage.jsx
│   │   │   ├── AnalyticsPage.jsx
│   │   │   ├── SystemPage.jsx
│   │   │   └── AuthPage.jsx     # ← UPDATED: GitHub button + callback
│   │   └── components/RepoCard.jsx
│   ├── package.json
│   └── vite.config.js
```

---

## 🔑 Key Notes

- Node.js path: `C:\Program Files\nodejs\` (not on system PATH)
- Backend: port 8000 | Frontend dev: port 5173
- Vite proxies `/api/*` → `http://127.0.0.1:8000`
- NIM key in `.env` as `NIM_API_KEY=nvapi-...`
- GitHub OAuth needs DB migration (new columns auto-created by SQLAlchemy on next startup)
