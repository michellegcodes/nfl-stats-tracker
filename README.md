# NFL Stats Tracker

A lightweight web app showing all 32 NFL teams with their logos, win/loss records, and win percentages for the current season. Data is pulled live from ESPN's public API on every page load.

![NFL Stats Tracker](https://img.shields.io/badge/NFL-Stats%20Tracker-013369?style=for-the-badge&logo=data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAyNCAyNCI+PHBhdGggZmlsbD0id2hpdGUiIGQ9Ik0xMiAyQzYuNDggMiAyIDYuNDggMiAxMnM0LjQ4IDEwIDEwIDEwIDEwLTQuNDggMTAtMTBTMTcuNTIgMiAxMiAyem0wIDE4Yy00LjQxIDAtOC0zLjU5LTgtOHMzLjU5LTggOC04IDggMy41OSA4IDgtMy41OSA4LTggOHoiLz48L3N2Zz4=)

## Features

- All 32 NFL teams displayed in a responsive card grid
- Team logos served directly from ESPN's CDN
- Win, loss (and tie) records for the current season
- Win percentage per team
- Live search bar — filters cards instantly as you type
- Dark NFL-themed UI with card hover effects

## Tech Stack

| Layer | Tool |
|---|---|
| Backend | [FastAPI](https://fastapi.tiangolo.com/) |
| Templating | Jinja2 |
| HTTP client | [httpx](https://www.python-httpx.org/) |
| Server | Uvicorn |
| Frontend | Vanilla HTML/CSS/JS (no framework) |
| Data source | ESPN public API (no key required) |

## Getting Started

### Prerequisites

- Python 3.9+

### Installation

```bash
git clone https://github.com/michellegcodes/nfl-stats-tracker.git
cd nfl-stats-tracker
pip install -r requirements.txt
```

### Run

```bash
python3 -m uvicorn main:app --reload
```

Open [http://localhost:8000](http://localhost:8000) in your browser.

## Project Structure

```
nfl-stats-tracker/
├── main.py              # FastAPI app and routes
├── espn.py              # ESPN API fetch + merge logic
├── templates/
│   └── index.html       # Jinja2 template — grid + search bar
├── static/
│   └── style.css        # Dark NFL-themed styles
└── requirements.txt
```

## Data Source

Two ESPN public endpoints are fetched on each page load and merged by team ID:

| Endpoint | Data |
|---|---|
| `site.api.espn.com/.../nfl/teams` | Team name, city, abbreviation, logo URL |
| `site.api.espn.com/.../nfl/standings` | Wins, losses, ties, win percentage |

No API key is required.
