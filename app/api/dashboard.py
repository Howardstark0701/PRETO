"""
Lightweight Phase 7 dashboard surface.
"""

from fastapi import APIRouter
from fastapi.responses import HTMLResponse


router = APIRouter(tags=["dashboard"])


DASHBOARD_HTML = """
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>PRETO Dashboard</title>
  <style>
    :root { color-scheme: light; font-family: Arial, sans-serif; }
    body { margin: 0; background: #f6f7f9; color: #172026; }
    header { background: #111827; color: white; padding: 18px 24px; }
    main { max-width: 1040px; margin: 0 auto; padding: 24px; }
    h1 { margin: 0; font-size: 24px; letter-spacing: 0; }
    h2 { font-size: 16px; margin: 0 0 12px; }
    .grid { display: grid; gap: 16px; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); }
    .panel, .repo { background: white; border: 1px solid #d9dee7; border-radius: 8px; padding: 16px; }
    label { display: block; font-size: 13px; font-weight: 700; margin-bottom: 6px; }
    input, select { box-sizing: border-box; width: 100%; border: 1px solid #aeb7c5; border-radius: 6px; padding: 10px; font-size: 14px; }
    button { border: 0; border-radius: 6px; background: #0f766e; color: white; padding: 10px 14px; font-weight: 700; cursor: pointer; }
    .row { display: grid; gap: 10px; grid-template-columns: 1fr 120px; align-items: end; }
    .stack { display: grid; gap: 12px; }
    .muted { color: #5b6675; font-size: 13px; }
    .repos { display: grid; gap: 10px; margin-top: 16px; }
    .repo h3 { margin: 0 0 6px; font-size: 15px; }
    .stats { display: flex; flex-wrap: wrap; gap: 10px; font-size: 13px; color: #334155; }
    pre { overflow: auto; white-space: pre-wrap; background: #172026; color: #e5e7eb; border-radius: 8px; padding: 12px; min-height: 120px; }
  </style>
</head>
<body>
  <header><h1>PRETO</h1><div class="muted">Repository intelligence workspace</div></header>
  <main>
    <div class="grid">
      <section class="panel stack">
        <h2>Search Repositories</h2>
        <label for="query">Query</label>
        <div class="row"><input id="query" value="python osint" /><button onclick="searchRepos()">Search</button></div>
        <label for="language">Language</label>
        <select id="language"><option value="">Any</option><option>Python</option><option>JavaScript</option><option>Go</option><option>Rust</option></select>
      </section>
      <section class="panel stack">
        <h2>User Repositories</h2>
        <label for="username">GitHub Username</label>
        <div class="row"><input id="username" value="torvalds" /><button onclick="loadUser()">Load</button></div>
      </section>
    </div>
    <section class="panel" style="margin-top:16px;">
      <h2>Results</h2>
      <div id="summary" class="muted">Ready.</div>
      <div id="results" class="repos"></div>
      <pre id="raw"></pre>
    </section>
  </main>
  <script>
    const resultBox = document.getElementById("results");
    const rawBox = document.getElementById("raw");
    const summary = document.getElementById("summary");

    async function fetchJson(url) {
      summary.textContent = "Loading...";
      resultBox.innerHTML = "";
      rawBox.textContent = "";
      const response = await fetch(url);
      const data = await response.json();
      rawBox.textContent = JSON.stringify(data, null, 2);
      if (!response.ok) throw new Error(data.detail || "Request failed");
      return data;
    }

    function renderRepos(repos) {
      resultBox.innerHTML = repos.map(repo => `
        <article class="repo">
          <h3>${repo.full_name || repo.name}</h3>
          <div class="muted">${repo.description || "No description"}</div>
          <div class="stats">
            <span>Stars: ${repo.stargazers_count || 0}</span>
            <span>Forks: ${repo.forks_count || 0}</span>
            <span>Language: ${repo.language || "Unknown"}</span>
          </div>
        </article>
      `).join("");
    }

    async function searchRepos() {
      try {
        const q = encodeURIComponent(document.getElementById("query").value);
        const lang = document.getElementById("language").value;
        const url = `/api/repos/search/advanced?query=${q}&per_page=10${lang ? `&language=${encodeURIComponent(lang)}` : ""}`;
        const data = await fetchJson(url);
        renderRepos(data.results || []);
        summary.textContent = `${data.pagination?.total_count || 0} results`;
      } catch (error) {
        summary.textContent = error.message;
      }
    }

    async function loadUser() {
      try {
        const user = encodeURIComponent(document.getElementById("username").value);
        const data = await fetchJson(`/api/repos/user/${user}?per_page=10`);
        renderRepos(data.repos || []);
        summary.textContent = `${data.total_count || 0} repositories for ${data.username}`;
      } catch (error) {
        summary.textContent = error.message;
      }
    }
  </script>
</body>
</html>
"""


@router.get("/dashboard", response_class=HTMLResponse)
async def dashboard():
    """Render the lightweight PRETO dashboard."""
    return HTMLResponse(DASHBOARD_HTML)
