<div align="center">

# 🔍 PRETO

### Open-Source OSINT & Public Data Intelligence Platform

*Palantir-inspired. Built on free APIs. Deployed by a college student.*

[![Live Demo](https://img.shields.io/badge/🌐_Live_Demo-preto.onrender.com-00d4b4?style=for-the-badge)](https://preto.onrender.com)
[![API Docs](https://img.shields.io/badge/📚_API_Docs-/api/docs-3b82f6?style=for-the-badge)](https://preto.onrender.com/api/docs)
[![GitHub](https://img.shields.io/badge/GitHub-Howardstark0701%2FPRETO-181717?style=for-the-badge&logo=github)](https://github.com/Howardstark0701/PRETO)

![Python](https://img.shields.io/badge/Python-3.11-3776AB?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.111-009688?logo=fastapi&logoColor=white)
![React](https://img.shields.io/badge/React-18-61DAFB?logo=react&logoColor=black)
![NVIDIA NIM](https://img.shields.io/badge/NVIDIA_NIM-Multi_Model-76B900?logo=nvidia&logoColor=white)
![Deployed on Render](https://img.shields.io/badge/Deployed-Render-46E3B7?logo=render&logoColor=white)

</div>

---

## What is PRETO?

Ever wanted to **understand a GitHub user's entire ecosystem at a glance**? Or ask an AI *"What are the most promising OSINT tools built in Python this year?"* and get a real, data-backed answer?

That's PRETO.

It's an **OSINT and public data intelligence platform** that aggregates GitHub data, runs AI analysis on it, and presents everything through a sleek Palantir-inspired dark dashboard. No paywalls. No proprietary lock-in. Just clean data and smart insights.

> Built as a college project to demonstrate full-stack engineering, AI integration, and production deployment — all in one repo.

---

## ✨ What Can It Do?

### 🔎 Search & Discover
Search GitHub repositories with advanced filters — language, star count, date range. Get paginated results with rich metadata. Save searches for later.

### 🕸️ Graph Analysis
The coolest part. Enter any GitHub username and watch a **live force-directed network graph** render their entire ecosystem — repositories, programming languages, and contributors — all connected, draggable, zoomable, and clickable.

Filter by language. Filter by star count. Click any node to see details. It's like a social network graph but for code.

### 🤖 AI Insights (NVIDIA NIM — Multi-Model)
Ask questions in plain English:
- *"Which repos show signs of active maintenance?"*
- *"What's the technology footprint of this user?"*
- *"Summarize the top trending OSINT tools"*

Powered by **NVIDIA NIM** with 4 selectable models — switch between Llama 3.1 70B, Llama 3.1 8B, Mixtral 8x22B, or Nemotron 4 340B. Preference is saved to your browser.

### 🌐 Multi-Source Intelligence
Search beyond GitHub — **GitLab**, **Reddit**, **Hacker News**, **X (Twitter)**, and **Dev.to** — all in one tabbed interface. Profile stats, activity feeds, and normalized results per source.

### 📊 Analytics
Bar charts, pie charts, trend lines. See stars vs forks, language distribution, activity scoring. Track what's trending in your searches over time.

### 📤 Export
Download your intelligence as **JSON**, **CSV**, or a formatted **PDF report**. Because data is only useful if you can share it.

### 🔐 Authentication
Full auth system — register/login with JWT, or one-click **GitHub OAuth**. Your searches and saved data persist across sessions.

---

## 🖥️ Interface

PRETO uses a **brutalist Palantir-inspired dark UI** — Space Grotesk headings, Karla body text, JetBrains Mono for data. Sharp 0px corners, flat HUD aesthetic, high information density.

```
┌─────────────────────────────────────────────────────────────┐
│  PRETO    INTELLIGENCE PLATFORM                             │
├──────────┬──────────────────────────────────────────────────┤
│          │                                                  │
│  🔍 Search│   [Search results with filters and pagination]  │
│  👤 User  │                                                  │
│  🕸️ Graph │   [Force-directed network of repos/langs/contribs│
│  🤖 AI    │   [Multi-model NIM chat + analysis]             │
│  🌐 Sources  [GitLab · Reddit · HN · X · Dev.to]           │
│  📊 Analytics  [Recharts bar/pie + export buttons]          │
│  ⚙️ System│                                                  │
│  🔐 Auth  │   [JWT login + GitHub OAuth]                    │
│          │                                                  │
│  ● API LIVE                                                 │
└──────────┴──────────────────────────────────────────────────┘
```

---

## 🚀 Tech Stack

| Layer | Technology | Why |
|-------|-----------|-----|
| **Backend** | FastAPI + Python 3.11 | Async, fast, auto-docs |
| **Database** | SQLite + SQLAlchemy | Zero-config, portable |
| **Auth** | JWT + GitHub OAuth 2.0 | Industry standard |
| **AI** | NVIDIA NIM (4 models: Llama/Mixtral/Nemotron) | Multi-model selector, localStorage persistence |
| **Frontend** | React 18 + Vite | Fast builds, modern DX |
| **Charts** | Recharts | Composable, responsive |
| **Graph** | D3.js v7 force simulation | The real deal for network graphs |
| **Styling** | Custom CSS (dark theme) | Palantir aesthetic |
| **Deployment** | Render + Docker | Free tier, auto-deploy |
| **CI/CD** | GitHub Actions | Test → Build → Deploy |

---

## 📡 API — 50+ Endpoints

<details>
<summary><b>Repositories</b> (5 endpoints)</summary>

```
GET  /api/repos/user/{username}           All repos for a user
GET  /api/repos/user/{username}/stats     User statistics
GET  /api/repos/search                    Basic search
GET  /api/repos/search/advanced           Paginated + filtered search
GET  /api/repos/{owner}/{repo}            Single repo details
```
</details>

<details>
<summary><b>Authentication</b> (8 endpoints)</summary>

```
POST /api/auth/register                   Create account
POST /api/auth/login                      Login → JWT
POST /api/auth/refresh                    Refresh token
GET  /api/auth/me                         Current user
GET  /api/auth/github                     GitHub OAuth redirect
GET  /api/auth/github/callback            OAuth callback → JWT
GET  /api/auth/saved-searches             List saved searches
POST /api/auth/saved-searches             Save a search
```
</details>



<details>
<summary><b>Advanced Analytics</b> (5 endpoints)</summary>

```
POST /api/advanced/analytics              Repository analytics engine
POST /api/advanced/export                 Export JSON / CSV
POST /api/advanced/export/pdf             Export PDF report
GET  /api/advanced/search-trends          Top trending searches
GET  /api/repos/{owner}/{repo}/contributors  Contributor data
```
</details>

<details>
<summary><b>System</b> (3 endpoints)</summary>

```
GET  /api/health                          Health check
GET  /api/metrics                         Prometheus metrics
GET  /                                    API info
```
</details>

<details>
<summary><b>Data Sources</b> (12 endpoints)</summary>

```
GET  /api/sources/gitlab/users/{username}                GitLab profile
GET  /api/sources/gitlab/users/{username}/projects       GitLab projects
GET  /api/sources/reddit/users/{username}                Reddit profile
GET  /api/sources/reddit/users/{username}/submissions    Reddit posts
GET  /api/sources/hackernews/users/{username}            HN profile
GET  /api/sources/hackernews/users/{username}/submissions HN posts
GET  /api/sources/x/users/{username}                     X profile
GET  /api/sources/x/users/{username}/tweets              X tweets
GET  /api/sources/devto/users/{username}                 Dev.to profile
GET  /api/sources/devto/users/{username}/articles        Dev.to articles
GET  /api/repos/trending                                 Trending repos
```
</details>

<details>
<summary><b>AI Insights</b> (5 endpoints)</summary>

```
GET  /api/insights/health                 NIM service status
GET  /api/insights/models                 Available AI models
POST /api/insights/analyze                Analyze repositories
POST /api/insights/query                  Natural language query
POST /api/insights/user-analysis          Analyze a GitHub user
```
</details>

**Full interactive docs**: https://preto.onrender.com/api/docs

---

## 🛠️ Running Locally

### Prerequisites
- Python 3.11+
- Node.js 18+

### 1. Clone & setup

```bash
git clone https://github.com/Howardstark0701/PRETO.git
cd PRETO

# Python environment
python -m venv venv
source venv/Scripts/activate      # Git Bash on Windows
# source venv/bin/activate         # macOS/Linux

pip install -r requirements.txt
```

### 2. Configure environment

```bash
cp .env.example .env
```

Open `.env` and fill in:

```env
GITHUB_TOKEN=github_pat_...          # github.com/settings/tokens
NIM_API_KEY=nvapi-...                # build.nvidia.com
SECRET_KEY=any-random-string-here
```

Everything else has sensible defaults for local dev.

### 3. Start backend

```bash
python main.py
```

→ API at `http://localhost:8000`  
→ Docs at `http://localhost:8000/api/docs`

### 4. Start frontend

```bash
cd frontend
npm install
npm run dev
```

→ UI at `http://localhost:5173`

---

## 🐳 Docker

```bash
# One command to run everything
docker-compose up --build
```

→ App at `http://localhost:8000`

---

## ☁️ Deploy Your Own Instance

PRETO has a `render.yaml` — fork the repo and deploy to Render in under 5 minutes.

1. Fork this repo
2. Go to [render.com](https://render.com) → New Web Service → connect your fork
3. Add your environment variables (see `.env.example`)
4. Hit deploy

Every push to `master` auto-deploys. See [DEPLOYMENT_GUIDE.md](./DEPLOYMENT_GUIDE.md) for the detailed walkthrough including all the issues we hit and how we fixed them.

---

## 🏗️ Project Structure

```
PRETO/
├── main.py                      # App entry point + static file serving
├── requirements.txt             # Pinned Python deps
├── Dockerfile                   # Multi-stage: Node build + Python prod
├── render.yaml                  # One-click Render deploy
│
├── app/
│   ├── api/
│   │   ├── routes.py            # Repo endpoints
│   │   ├── auth_routes.py       # JWT auth endpoints
│   │   ├── github_oauth.py      # GitHub OAuth 2.0 flow
│   │   ├── insights.py          # NVIDIA NIM client + rate limiter
│   │   ├── insights_routes.py   # AI endpoints
│   │   ├── advanced_routes.py   # Analytics + export
│   │   ├── advanced_features.py # PDF, CSV, analytics engine
│   │   ├── middleware.py        # Rate limiting + security headers
│   │   ├── metrics.py           # Thread-safe Prometheus collector
│   │   ├── cache.py             # In-memory + DB caching
│   │   ├── crud.py              # Database operations
│   │   ├── scheduler.py         # APScheduler background jobs
│   │   └── logging_config.py    # Structured JSON logging
│   ├── models/
│   │   ├── database.py          # SQLAlchemy setup
│   │   └── auth.py              # User + OAuth model
│   └── scrapers/
│       ├── github_scraper.py    # Async GitHub API client
│       ├── gitlab_scraper.py    # GitLab API client
│       ├── reddit_scraper.py    # Reddit API client
│       ├── hackernews_scraper.py # Hacker News Firebase API
│       ├── x_scraper.py         # X/Twitter profile scraper
│       └── devto_scraper.py     # Dev.to API client
│
├── frontend/
│   └── src/
│       ├── api.js               # All 34 endpoints in one file
│       ├── App.jsx              # Router + sidebar
│       └── pages/
│           ├── SearchPage.jsx
│           ├── UserPage.jsx
│           ├── GraphPage.jsx    # D3 force graph
│           ├── AnalyticsPage.jsx
│           ├── InsightsPage.jsx
│           ├── SourcesPage.jsx  # Multi-source intelligence
│           ├── SystemPage.jsx
│           └── AuthPage.jsx
│
└── tests/
    └── test_health.py           # 5 integration tests
```

---

## 🗺️ Roadmap

- [ ] PostgreSQL for persistent production storage
- [ ] Redis caching layer
- [ ] Multi-user graph comparison
- [ ] Additional data sources (npm registry, PyPI)
- [ ] Full unit test suite (target 80% coverage)
- [x] Multi-model AI selector (4 NIM models)
- [x] Multi-source intelligence (GitLab, Reddit, HN, X, Dev.to)
- [x] Stitch UI redesign (sharp 0px, brutalist aesthetic)

---

## 🤝 Contributing

Pull requests are welcome. For major changes, open an issue first to discuss what you'd like to change.

```bash
# Create a feature branch
git checkout -b feature/your-feature-name

# Make your changes, then
git commit -m "feat: describe your change"
git push origin feature/your-feature-name

# Open a pull request on GitHub
```

---

## 📄 License

MIT — free to use, modify, and distribute.

---

<div align="center">

Built with 🔥 by [TANGO](https://github.com/Howardstark0701)

*FastAPI · React · NVIDIA NIM · D3.js · Deployed on Render*

**Star the repo if you find it useful ⭐**

</div>
