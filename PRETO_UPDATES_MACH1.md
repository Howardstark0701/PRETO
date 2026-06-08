# PRETO_UPDATES_MACH1

> **Evolution Blueprint** — Fonts, Logo, UI Redesign, New Data Sources, Multi-Model AI
> Palantir-inspired OSINT platform. Built on free APIs. Deployed by a college student.

---

## Table of Contents

1. [Font Overhaul](#1-font-overhaul)
2. [Logo Direction](#2-logo-direction)
3. [Google Stitch UI Redesign](#3-google-stitch-ui-redesign)
4. [New Data Sources](#4-new-data-sources)
5. [Multi-Model AI Selector](#5-multi-model-ai-selector)
6. [Execution Roadmap](#6-execution-roadmap)
7. [File Manifest](#7-file-manifest)

---

## 1. Font Overhaul

### Problem
The current site uses `JetBrains Mono` (monospace) for **everything** — headings, nav, buttons, form labels, body text, code blocks. While it fits the "terminal" aesthetic, it hurts readability, lacks visual hierarchy, and makes every page look flat.

### Solution — Three-Tier Font System

| Tier | Font | Category | Used For |
|------|------|----------|----------|
| **Headings / Display** | `'Space Grotesk', sans-serif` | Geometric sans-serif | `.page-title`, `.panel-title`, `.stat-val`, `.logo-text`, `h1`–`h4`, all display text |
| **UI / Nav / Body** | `'Karla', sans-serif` | Humanist sans-serif | `.nav-item`, `.form-label`, `.btn`, `.badge`, `.tab`, `.data-table th`, `.page-sub`, `.sidebar-label`, `.form-input`, `.sidebar-footer`, general body text |
| **Data / Code** | `'JetBrains Mono', 'Fira Code', 'Consolas', monospace` | Monospace (sparingly) | `.code-block`, `.data-table td`, stat numbers, terminal output, raw data |

### Why These Three?

- **Space Grotesk** — Geometric, slightly quirky, very unique. Feels like a modern intelligence agency's dashboard. Visibly different from both Karla and JetBrains Mono.
- **Karla** — Warm humanist sans-serif with character (notice the quirky `a`, `g`, `t`). Created specifically for UI readability at small sizes (10–14px). Provides maximum **contrast** against Space Grotesk — they don't look alike at all.
- **JetBrains Mono** — Already excellent. Reserve it for where it genuinely belongs: data tables, code blocks, stat values. No longer used for nav, buttons, or form elements.

### Implementation

#### `frontend/src/index.css`
```css
:root {
  /* ── Typography ── */
  --font-heading: 'Space Grotesk', sans-serif;
  --font-ui:      'Karla', sans-serif;
  --font-mono:    'JetBrains Mono', 'Fira Code', 'Consolas', monospace;
}

html, body, #root {
  font-family: var(--font-ui);   /* Karla by default */
}

button, input, select, textarea {
  font-family: var(--font-ui);   /* Karla, not monospace */
}
```

#### `frontend/src/App.css`
Add `font-family: var(--font-heading)` to:
- `.page-title`
- `.panel-title`
- `.stat-val`
- `.logo-text`
- `.sidebar-logo .logo-text`

All other classes inherit `--font-ui` from `body`.

#### `frontend/index.html`
```html
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600;700&family=Karla:ital,wght@0,300;0,400;0,500;0,600;0,700;1,400&display=swap" rel="stylesheet">
```

---

## 2. Logo Direction

### Philosophy
Abstract only. No letters, no monograms, no OSINT tropes (no eyes, no radar arcs, no network nodes, no magnification glasses). The logo should feel **hand-crafted, not AI-generated** — raw, deliberate, architectural.

### Design Principle
Inspired by the same restraint that makes Palantir's logo work: subtle, minimal, no forced symbolism. Pure geometric abstraction.

### Constraints
- Monochromatic with optional teal accent (`#00d4b4`)
- Must work at 16px (favicon) and 200px (sidebar)
- SVG format, scalable
- No text in the mark itself

### Creation Process
The logo will be designed in **Google Stitch** as part of the full UI redesign session (Phase 2). We iterate on shape, proportion, and weight until it feels right — no forcing a concept prematurely.

### Fallback
If Stitch doesn't produce satisfactory results, use **BRUTAFORM** (GPT-powered brutalist SVG logo generator at `https://brutaform.com/`) to generate raw geometric candidates in pure SVG.

---

## 3. Google Stitch UI Redesign

### Tool
[Google Stitch](https://stitch.withgoogle.com/) — AI-powered UI design canvas from Google Labs. Uses Gemini models (developer has Gemini Pro access). Generates high-fidelity mockups from natural language that can be exported as DESIGN.md + frontend code.

### Stitch Prompt (Seed)

```
Project: PRETO — Open Source Intelligence Dashboard

Brand:
- Name: PRETO
- Tagline: "Open Source Intelligence Platform"
- Vibe: Palantir-inspired, analytical, professional, dense with information
- Not: futuristic/sci-fi, not cyberpunk, not gimmicky

Typography:
- Headings: Space Grotesk (geometric sans-serif)
- UI/Body: Karla (humanist sans-serif, warm and readable)
- Data/Code: JetBrains Mono (monospace, used sparingly)

Color Palette:
- bg-base:       #0b0e14 (very dark blue-black)
- bg-panel:      #111827 (dark panel)
- bg-card:       #161d2e (card surface)
- bg-hover:      #1e2a40 (hover state)
- border:        #1f2d45 (subtle borders)
- border-light:  #2a3a55 (lighter borders)
- accent:        #00d4b4 (teal — primary accent)
- accent-dim:    #00907a (dimmed teal)
- accent2:       #3b82f6 (blue — secondary accent)
- danger:        #ef4444 (red)
- warn:          #f59e0b (yellow/amber)
- text-primary:  #e2e8f0 (main text)
- text-muted:    #64748b (secondary text)
- text-dim:      #94a3b8 (dim text)

Layout:
- Fixed left sidebar (200px, collapsible on mobile)
- Main content area with max-width 1280px
- Panel-based card system with consistent padding/borders
- Tab navigation for multi-view pages

Pages to Design:
1. SearchPage — GitHub repository search with filters, pagination, optional AI insights
2. UserPage — User stats, language bar chart, AI profile analysis
3. GraphPage — Force-directed D3.js network graph (user → repos → languages → contributors)
4. InsightsPage — AI chat interface (NVIDIA NIM), model selector dropdown, two tabs: NL query + repo analysis
5. AnalyticsPage — Charts (Recharts), search trends, export (JSON/CSV/PDF)
6. SystemPage — Live monitoring: API health, cache stats, scheduler status, sync stats
7. AuthPage — Login/register, GitHub OAuth, saved searches, history, API keys

Design System:
- Small border-radius (4–6px) — utilitarian, not rounded
- Tight letter-spacing on labels and metadata
- Uppercase + muted color for secondary labels
- Monospace for all data values, code, and table cells
- Teal accent for interactive elements, blue for tags/metadata
- Red for errors/danger, amber for warnings
- Subtle hover transitions on cards and interactive elements
- Loading skeleton states (not just spinners)
```

### Pages to Iterate On

| Page | Current Issues | Stitch Improvements |
|------|---------------|-------------------|
| **Sidebar** | Fixed 200px, no collapse, basic nav | Collapsible, sub-nav sections, user avatar at bottom, cleaner spacing |
| **SearchPage** | Basic form layout, plain results | Better filter row (inline + collapsible), inline repo preview, AI insight panel |
| **UserPage** | Stats feel cramped | Larger stat boxes, better language chart layout, AI profile as a sidebar card |
| **GraphPage** | D3 is functional but plain | Darker canvas, node glow effects, better tooltip, legend panel |
| **InsightsPage** | Basic chat UI, no model choice | Proper chat interface (message bubbles, timestamps), model selector dropdown, code formatting |
| **AnalyticsPage** | Charts work but lack polish | Better chart sizing, export button placement, trend visual indicators |
| **SystemPage** | Grid of basic cards | Gauge widgets, progress bars, live-updating indicators, last-updated timestamps |
| **AuthPage** | Stacked forms, cramped | Split layout (form left, info right), cleaner OAuth button, saved search cards |

### Post-Stitch Integration
1. Export DESIGN.md from Stitch (all design tokens, colors, spacing rules)
2. Export component code/screenshots for each page
3. Implement React components matching the new design
4. Update CSS variables to match Stitch's output

---

## 4. New Data Sources

### Priority & Rationale

| # | Source | API | Auth | Complexity | Why |
|---|--------|-----|------|------------|-----|
| 1 | **GitLab** | `gitlab.com/api/v4` | Public token (optional) | Medium | Most similar to GitHub — reuse scraper architecture. Huge OSINT value. |
| 2 | **Reddit** | `reddit.com/api` via OAuth | OAuth (free) | Easy | User activity, subreddit insights, posting patterns. Fun, relatable data. |
| 3 | **Hacker News** | Firebase API (`hacker-news.firebaseio.com`) | None | Very Easy | Zero auth, rich user data (karma, submissions, comments). Best effort-to-value ratio. |
| 4 | **X (Twitter)** | Public profile endpoints | Bearer token (free tier) | Medium | Public profile analysis, follower counts, recent tweets. High OSINT value. |
| 5 | **Dev.to** | `dev.to/api` | Optional API key | Very Easy | Developer community data, article stats, user tags. Clean REST API. |
| 6 | **GitHub enhancements** | Existing GitHub API | Existing token | Easy | Trending repos, starred repo analysis, contributor heatmaps, org-level insights. |

### Architecture Pattern

Each new source follows the same template:

```
app/scrapers/
├── github_scraper.py    (existing — reference implementation)
├── gitlab_scraper.py    (new)
├── reddit_scraper.py    (new)
├── hackernews_scraper.py (new)
├── x_scraper.py         (new)
└── devto_scraper.py     (new)
```

Each scraper:
- Uses `httpx.AsyncClient` for async HTTP
- Implements built-in rate limiting
- Returns normalized data matching existing Repository/User schemas
- Caches results via existing CacheService
- Logs via existing structured logging

### Backend Endpoints

```
GET  /api/sources/gitlab/users/{username}
GET  /api/sources/gitlab/users/{username}/projects
GET  /api/sources/reddit/users/{username}
GET  /api/sources/reddit/users/{username}/submissions
GET  /api/sources/hackernews/users/{username}
GET  /api/sources/hackernews/users/{username}/submissions
GET  /api/sources/x/users/{username}
GET  /api/sources/x/users/{username}/tweets
GET  /api/sources/devto/users/{username}
GET  /api/sources/devto/users/{username}/articles
```

### Frontend
New **"Sources"** page or tab in SearchPage:
- Multi-source search bar (select source from dropdown)
- Results in existing card/table patterns
- Source badge on each result (GitLab blue, Reddit orange, HN orange, X black, Dev.to purple)

---

## 5. Multi-Model AI Selector

### Problem
Currently hardcoded to a single model at `insights.py:22`:
```python
NIM_MODEL = os.getenv("NIM_MODEL", "meta/llama-3.1-70b-instruct")
```
Users have zero choice. The AI either works with Llama 3.1 70B or falls back to basic statistics.

### Why Include in MACH1
- The code change is **minimal** (~2 hours): add a `model` field to requests, pass it through to the NIM API call, add a dropdown in the frontend.
- Stitch redesign of InsightsPage should **already include** the model selector — retrofitting later means redesigning the page twice.

### Approach: NIM Model Selection

NVIDIA NIM serves multiple models through the same OpenAI-compatible endpoint. The model is just a string in the request body. We let users pick from a curated list.

### Proposed Models

| Model | When to use |
|-------|-------------|
| `meta/llama-3.1-70b-instruct` | **Default** — balanced power and speed for most tasks |
| `meta/llama-3.1-8b-instruct` | **Fast** — quick lookups, simple queries (3-4x faster) |
| `mistralai/mixtral-8x22b-instruct-v0.1` | **Alternative** — different architecture, strong at analysis |
| `nvidia/nemotron-4-340b-instruct` | **Deep** — maximum power for comprehensive analysis (if available) |

### Backend Changes

**`insights_schemas.py`** — Add optional `model` field to request schemas:
```python
model: str = "meta/llama-3.1-70b-instruct"
```

**`insights.py`**:
- Add `ALLOWED_MODELS` list for validation
- Pass `model` from request → `_call_nim()` → request body `"model"` field
- Add `GET /api/insights/models` endpoint returning available options

**`insights_routes.py`**:
```python
@router.get("/models")
async def get_available_models():
    return {
        "models": ALLOWED_MODELS,
        "default": "meta/llama-3.1-70b-instruct"
    }
```

### Frontend Changes

**`InsightsPage.jsx`**:
- Fetch available models on mount via `GET /api/insights/models`
- Add dropdown/select next to query input and analyze button:
  ```
  [Model: Llama 3.1 70B ▼] [Ask NIM]
  ```
- Persist user's preference in `localStorage`
- Pass selected model in request bodies

### Future: BYO API Key (Post-MACH1)
Authenticated users could store their own OpenAI/Anthropic/Gemini API keys in the DB (encrypted). Backend routes to the appropriate provider based on model selection. Not in MACH1 scope.

---

## 6. Execution Roadmap

```
Week 1: Phase 1 — Font Implementation ✅ COMPLETE
  ├── Add Google Fonts links to frontend/index.html
  ├── Update frontend/src/index.css with --font-heading, --font-ui, --font-mono
  ├── Update frontend/src/App.css with font-family declarations per class
  └── Review all 7 pages for font consistency

Week 2: Phase 2 — Logo + Stitch UI Redesign ✅ COMPLETE
  ├── Create Stitch project with seed prompt
  ├── Design all 7 pages + sidebar + logo
  ├── Iterate logo (abstract, brutalist, no letters) — TBD in Stitch
  ├── Export DESIGN.md + design tokens
  └── Apply design tokens to CSS (colors, typography scale, sharp corners)

Week 3: Phase 3 — Stitch Integration (refinements) ✅ COMPLETE
  ├── CSS already updated with design tokens
  ├── Rebuild components per new designs if needed
  ├── Add micro-animations & loading skeletons
  ├── Test responsive behavior (mobile sidebar collapse)
  └── Deploy and review

Week 4: Phase 4a — GitLab Scraper ✅ COMPLETE
  ├── Create gitlab_scraper.py
  ├── Add GitLab API endpoints
  ├── Add GitLab UI (SourcesPage tab)
  ├── Test with real GitLab usernames
  └── Deploy

Week 5: Phase 4b — Reddit + Hacker News ✅ COMPLETE
  ├── Create reddit_scraper.py
  ├── Create hackernews_scraper.py
  ├── Add API endpoints for both
  ├── Add UI for both
  └── Deploy

Week 6: Phase 4c + Phase 5 — X, Dev.to, GitHub Enhancements + Multi-Model AI ✅ COMPLETE
  ├── Create x_scraper.py
  ├── Create devto_scraper.py
  ├── Add GitHub trending/starred endpoints
  ├── Add UI for all three
  ├── Implement multi-model AI selector (backend + frontend)
  ├── Full integration testing
  └── Deploy
```

---

## 7. File Manifest

### Files Created
| File | Phase | Purpose |
|------|-------|---------|
| `DESIGN.md` | 2 | Stitch design tokens export (colors, typography, spacing, components) |
| `app/scrapers/gitlab_scraper.py` | 4a | GitLab API client |
| `app/scrapers/reddit_scraper.py` | 4b | Reddit API client |
| `app/scrapers/hackernews_scraper.py` | 4b | Hacker News Firebase API client |
| `app/scrapers/x_scraper.py` | 4c | X/Twitter profile scraper |
| `app/scrapers/devto_scraper.py` | 4c | Dev.to API client |

### Files Modified
| File | Phase | Changes |
|------|-------|---------|
| `frontend/index.html` | 1 | Added Google Fonts link tags for Space Grotesk + Karla |
| `frontend/src/index.css` | 1, 2 | Font variables + Stitch color tokens + typography scale + sharp corners |
| `frontend/src/App.css` | 1, 2 | Heading font on `.page-title`, `.panel-title`, `.stat-val`, `.logo-text`. All rounded corners → `var(--radius)` = 0px. |
| `app/api/insights.py` | 5 | Add `ALLOWED_MODELS`, `get_available_models()`, pass `model` param to NIM call |
| `app/api/insights_routes.py` | 5 | Add `GET /api/insights/models` endpoint. Pass `model` from request body. |
| `app/api/insights_schemas.py` | 5 | Add optional `model: str` field to request schemas |
| `frontend/src/pages/InsightsPage.jsx` | 5 | Add model selector dropdown. Fetch models on mount. Pass model to API calls. |
| `frontend/src/pages/*.jsx` (all 7) | 3 | Rebuild per new design system |
| `frontend/src/App.jsx` | 3 | If sidebar layout changes |
| `frontend/src/components/RepoCard.jsx` | 3 | Update per new design system |
| `app/api/routes.py` | 4 | Add source-specific endpoints |
| `app/api/schemas.py` | 4 | Add source-specific Pydantic models |

---

## Appendix: Current State (Baseline)

| Aspect | Pre-MACH1 | Post-MACH1 | Status |
|--------|-----------|------------|--------|
| **Heading font** | JetBrains Mono | Space Grotesk | ✅ Done |
| **UI/Body font** | JetBrains Mono | Karla | ✅ Done |
| **Data/Code font** | JetBrains Mono everywhere | JetBrains Mono (sparingly) | ✅ Done |
| **Logo** | Text "P RETO" | Abstract mark (TBD in Stitch) | 🔲 Pending |
| **Color palette** | Original dark theme | Stitch DESIGN.md tokens | ✅ Done |
| **Corners** | 4-6px rounded | Sharp 0px (brutalist) | ✅ Done |
| **Design tokens** | None | DESIGN.md exported from Stitch | ✅ Done |
| **AI models** | 1 (Llama 3.1 70B) | 4 curated NIM models + user selector | ✅ Done |
| **Data sources** | GitHub only | GitHub + GitLab + Reddit + HN + X + Dev.to | ✅ Done |
| **Scrapers** | 1 | 6 | ✅ Done |
| **UI pages** | 7 | 7 (+ SourcesPage) | ✅ Done |
| **InsightsPage Activity Feed** | Basic list timeline | Source filter pills, GitHub integration, shared inset toggle with teal top-border active state, grouped date headers, platform-colored timeline dots, scrollable feed | ✅ Done |

---

*Planned:7 June 2026*
*Built by TANGO*
