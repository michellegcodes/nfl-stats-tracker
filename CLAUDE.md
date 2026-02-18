# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
# Install dependencies
pip install -r requirements.txt

# Run the dev server (auto-reloads on file changes)
python3 -m uvicorn main:app --reload

# App runs at http://localhost:8000
```

There is no test suite, linter, or build step configured.

## Architecture

This is a FastAPI web app that displays NFL team standings and detail pages using live data from ESPN's public API. No API key is required.

**Request flow:** Browser → FastAPI route (`main.py`) → ESPN data functions (`espn.py`) → Jinja2 template → HTML response.

### Key modules

- **`main.py`** — Two routes: `GET /` (all teams grid) and `GET /team/{team_id}` (team detail page). Delegates all data fetching to `espn.py` and renders Jinja2 templates.
- **`espn.py`** — All ESPN API interaction and data transformation. Two main entry points:
  - `get_all_teams()` — Fetches from two ESPN endpoints (teams + standings), merges them by team ID, returns sorted list.
  - `fetch_team_detail(team_id)` — Fetches four ESPN endpoints concurrently via `asyncio.gather` (team info, stats, roster, league-wide stats), assembles a single dict with venue info, offense/defense stats, player leaders, and full roster.
  - `STADIUM_OPENED` dict provides stadium opening years (not available from ESPN API).
  - `LEADER_CATEGORIES` controls which stat categories appear on the detail page.

### Frontend

- **`templates/index.html`** — Team card grid with client-side search filtering (vanilla JS).
- **`templates/team.html`** — Team detail page with venue banner, season leaders, offense/defense stats tables, and roster. Uses CSS custom properties (`--team-primary`, `--team-alt`) set from ESPN team colors for the header gradient.
- **`static/style.css`** — Single stylesheet for both pages. Dark theme using CSS custom properties defined in `:root`.

### ESPN API endpoints used

| Endpoint | Used in |
|---|---|
| `site.api.espn.com/.../nfl/teams` | `fetch_teams()`, `fetch_team_detail()` |
| `site.api.espn.com/.../nfl/standings` | `fetch_standings()` |
| `site.api.espn.com/.../nfl/teams/{id}/statistics` | `fetch_team_detail()` |
| `site.api.espn.com/.../nfl/teams/{id}/roster` | `fetch_team_detail()` |
| `site.api.espn.com/.../nfl/statistics` | `fetch_team_detail()` (league-wide player leaders) |

All data is fetched fresh on every page load — there is no caching layer.
