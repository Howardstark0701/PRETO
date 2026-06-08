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
![NVIDIA NIM](https://img.shields.io/badge/NVIDIA_NIM-Multi--Model-76B900?logo=nvidia&logoColor=white)
![Deployed on Render](https://img.shields.io/badge/Deployed-Render-46E3B7?logo=render&logoColor=white)

</div>

---

## What is PRETO?

Ever wanted to **understand a developer's entire digital footprint at a glance**? Or ask an AI *"What are the most promising OSINT tools built in Python this year?"* and get a real, data-backed answer?

That's PRETO.

It's an **open-source OSINT and public data intelligence platform** that aggregates data from GitHub, GitLab, Reddit, Hacker News, X, and Dev.to — runs AI analysis on it — and presents everything through a sharp, Palantir-inspired dark dashboard. No paywalls. No proprietary lock-in.

> Built as a college project to demonstrate full-stack engineering, multi-source data aggregation, AI integration, and production deployment — all in one repo.

---

## ✨ Features

### 🔎 Multi-Source Intelligence
Search and aggregate public data across **6 platforms** from one interface:
- **GitHub** — repos, users, stats, contributors, trending
- **GitLab** — projects, user profiles
- **Reddit** — user activity, post history, subreddit analysis
- **Hacker News** — karma, submissions, comment history
- **X (Twitter)** — public profile stats, recent tweets
- **Dev.to** — articles, tags, follower stats

### 🕸️ Graph Analysis
Enter any GitHub username and watch a **live D3.js force-directed network** render their entire ecosystem — repositories, programming languages, and contributors — all connected, draggable, zoomable, and clickable. Filter by language and star count in real time.

### 🤖 Multi-Model AI (NVIDIA NIM)
Ask questions in plain English using your choice of 4 AI models:

| Model | Best For |
|-------|----------|
| Llama 3.1 70B | Default — balanced and thorough |
| Llama 3.1 8B | Fast lookups and quick queries |
| Mixtral 8x22B | Strong analytical reasoning |
| Nemotron 340B | Deep, comprehensive analysis |

Your model preference is saved automatically. 99% cheaper than GPT-4.

### 📊 Analytics
Recharts bar and pie charts, trend tracking, repository comparisons, and activity scoring. See what's actually moving in the data.

### 📤 Export
Download your intelligence as **JSON**, **CSV**, or a formatted **PDF report**.

### 🔐 Authentication
JWT register/login or one-click **GitHub OAuth**. Saved searches, search history, and API key management built in.

---

## 🎨 Design — MACH1 UI

PRETO was redesigned under **MACH1** with a full design system built in Google Stitch:

- **Space Grotesk** for headings and display text
- **Karla** for UI, navigation, and body copy
- **JetBrains Mono** reserved for data, code, and table values
- **Sharp 0px corners** — brutalist HUD aesthetic, not bubbly
- **Design tokens** from `DESIGN.md` — consistent color palette, spacing, and typography scale across all components

```
┌─────────────────────────────────────────────────────────────┐
│  P RETO    INTELLIGENCE PLATFORM              ● API LIVE    │
├──────────┬──────────────────────────────────────────────────┤
│  🔍 Search│                                                  │
│  👤 User  │   Sharp-cornered panels. Dense information.     │
│  🌐 Sources   Space Grotesk headings. Karla UI copy.        │
│  🕸️ Graph │   Teal accents. Dark blue-black background.     │
│  🤖 AI    │   D3 graph. Recharts. Multi-model selector.     │
│  📊 Analytics                                               │
│  ⚙️ System│                                                  │
│  🔐 Auth  │                                                  │
└──────────┴──────────────────────────────────────────────────┘
```

---

## 🚀 Tech Stack

| Layer | Technology | Why |
|-------|-----------|-----|
| **Backend** | FastAPI + Python 3.11 | Async, fast, auto-docs |
| **Database** | SQLite + SQLAlchemy | Zero-config, portable |
| **Auth** | JWT + GitHub OAuth 2.0 | Industry standard |
| **AI** | NVIDIA NIM (4 models) | 99% cheaper than Claude/GPT |
| **Frontend** | React 18 + Vite | Fast builds, modern DX |
| **Charts** | Recharts | Composable, responsive |
| **Graph** | D3.js v7 | Force simulation for network graphs |
| **Design** | Google Stitch + custom CSS | Palantir aesthetic |
| **Deployment** | Render + Docker | Free tier, auto-deploy |
| **CI/CD** | GitHub Actions | Test → Build → Deploy |

---

## 📡 API — 34+ Endpoints

<details>
<summary><b>Repositories</b></summary>

```
GET  /api/repos/user/{username}           User repositories
GET  /api/repos/user/{username}/stats     User statistics
GET  /api/repos/search                    Basic search
GET  /api/repos/search/advanced           Paginated + filtered search
GET  /api/repos/{owner}/{repo}            Single repo details
GET  /api/repos/{owner}/{repo}/contributors  Contributors
```
</details>

<details>
<summary><b>Multi-Source Intelligence</b></summary>

```
GET  /api/sources/gitlab/users/{username}
GET  /api/sources/gitlab/users/{username}/projects
GET  /api/sources/reddit/users/{username}
GET  /api/sources/hackernews/users/{username}
GET  /api/sources/x/users/{username}
GET  /api/sources/devto/users/{username}
GET  /api/sources/devto/users/{username}/articles
```
</details>

<details>
<summary><b>AI Insights (NVIDIA NIM)</b></summary>

```
GET  /api/insights/health                 NIM service status
GET  /api/insights/models                 Available AI models
POST /api/insights/analyze                Analyze repositories
POST /api/insights/query                  Natural language query
POST /api/insights/user-analysis          Analyze a GitHub user
```
</details>

<details>
<summary><b>Authentication</b></summary>

```
POST /api/auth/register
POST /api/auth/login
POST /api/auth/refresh
GET  /api/auth/me
GET  /api/auth/github                     OAuth redirect
GET  /api/auth/github/callback            OAuth → JWT
GET  /api/auth/saved-searches
POST /api/auth/saved-searches
```
</details>

<details>
<summary><b>Advanced Analytics</b></summary>

```
POST /api/advanced/analytics
POST /api/advanced/export                 JSON / CSV
POST /api/advanced/export/pdf             PDF report
GET  /api/advanced/search-trends
```
</details>

<details>
<summary><b>System</b></summary>

```
GET  /api/health
GET  /api/metrics                         Prometheus metrics
GET  /
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

python -m venv venv
source venv/Scripts/activate      # Git Bash on Windows
# source venv/bin/activate         # macOS/Linux

pip install -r requirements.txt
```

### 2. Configure environment

```bash
cp .env.example .env
# Edit .env with your keys
```

Minimum required:
```env
GITHUB_TOKEN=github_pat_...       # github.com/settings/tokens
NIM_API_KEY=nvapi-...             # build.nvidia.com
SECRET_KEY=any-random-string
```

### 3. Start backend

```bash
python main.py
# API:  http://localhost:8000
# Docs: http://localhost:8000/api/docs
```

### 4. Start frontend

```bash
cd frontend
npm install
npm run dev
# UI: http://localhost:5173
```

---

## 🐳 Docker

```bash
docker-compose up --build
# App at http://localhost:8000
```

---

## ☁️ Deploy Your Own

PRETO has a `render.yaml` — fork and deploy to Render in under 5 minutes.

1. Fork this repo
2. [render.com](https://render.com) → New Web Service → connect your fork
3. Add env vars from `.env.example`
4. Deploy

Auto-deploys on every push to `master`. See [DEPLOYMENT_GUIDE.md](./DEPLOYMENT_GUIDE.md) for the full walkthrough.

---

## 🏗️ Project Structure

```
PRETO/
├── main.py                      # FastAPI entry point
├── requirements.txt
├── Dockerfile                   # Multi-stage: Node + Python
├── render.yaml                  # One-click Render deploy
├── DESIGN.md                    # Stitch design tokens (MACH1)
│
├── app/
│   ├── api/
│   │   ├── routes.py            # Repo + sources endpoints
│   │   ├── auth_routes.py
│   │   ├── github_oauth.py
│   │   ├── insights.py          # NIM multi-model client
│   │   ├── insights_routes.py
│   │   ├── advanced_routes.py
│   │   ├── middleware.py        # Rate limiting + security headers
│   │   ├── metrics.py           # Prometheus collector
│   │   └── logging_config.py
│   ├── models/
│   └── scrapers/
│       ├── github_scraper.py
│       ├── gitlab_scraper.py    # MACH1
│       ├── reddit_scraper.py    # MACH1
│       ├── hackernews_scraper.py # MACH1
│       ├── x_scraper.py         # MACH1
│       └── devto_scraper.py     # MACH1
│
├── frontend/
│   └── src/
│       ├── api.js               # All endpoints
│       ├── App.jsx
│       └── pages/
│           ├── SearchPage.jsx
│           ├── UserPage.jsx
│           ├── GraphPage.jsx    # D3 force graph
│           ├── SourcesPage.jsx  # MACH1 — multi-source
│           ├── InsightsPage.jsx # MACH1 — model selector
│           ├── AnalyticsPage.jsx
│           ├── SystemPage.jsx
│           └── AuthPage.jsx
│
└── tests/
    └── test_health.py
```

---

## 🗺️ Roadmap

- [x] GitHub scraper + REST API
- [x] React dashboard (7 pages)
- [x] JWT + GitHub OAuth
- [x] NVIDIA NIM AI insights
- [x] D3 graph analysis
- [x] PDF/CSV/JSON export
- [x] Prometheus metrics + structured logging
- [x] Production deployment (Render)
- [x] **MACH1** — Multi-source (GitLab, Reddit, HN, X, Dev.to), Multi-model AI, Stitch UI redesign
- [ ] PostgreSQL for persistent production storage
- [ ] Redis caching layer
- [ ] Abstract SVG logo (brutalist, no letters)
- [ ] BYO API key (user-stored OpenAI/Anthropic keys)
- [ ] Full unit test suite (80%+ coverage)

---

## 🤝 Contributing

PRs are welcome. For major changes, open an issue first.

```bash
git checkout -b feature/your-feature
# make changes
git commit -m "feat: describe your change"
git push origin feature/your-feature
# open a pull request
```

---

## 📄 License

MIT — free to use, modify, and distribute.

---

<div align="center">

Built with 🔥 by [TANGO](https://github.com/Howardstark0701)

*FastAPI · React · NVIDIA NIM · D3.js · Google Stitch · Deployed on Render*

**Star the repo if you find it useful ⭐**

</div>
