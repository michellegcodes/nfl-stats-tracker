import asyncio
import httpx

TEAMS_URL = "https://site.api.espn.com/apis/site/v2/sports/football/nfl/teams"
STANDINGS_URL = "https://site.api.espn.com/apis/v2/sports/football/nfl/standings"
LEAGUE_STATS_URL = "https://site.api.espn.com/apis/site/v2/sports/football/nfl/statistics"

# Year each current NFL stadium opened (ESPN API does not expose this field)
STADIUM_OPENED: dict[str, int] = {
    "ARI": 2006,  # State Farm Stadium
    "ATL": 2017,  # Mercedes-Benz Stadium
    "BAL": 1998,  # M&T Bank Stadium
    "BUF": 1973,  # Highmark Stadium
    "CAR": 1996,  # Bank of America Stadium
    "CHI": 1924,  # Soldier Field
    "CIN": 2000,  # Paycor Stadium
    "CLE": 1999,  # Huntington Bank Field
    "DAL": 2009,  # AT&T Stadium
    "DEN": 2001,  # Empower Field at Mile High
    "DET": 2002,  # Ford Field
    "GB":  1957,  # Lambeau Field
    "HOU": 2002,  # NRG Stadium
    "IND": 2008,  # Lucas Oil Stadium
    "JAX": 1995,  # EverBank Stadium
    "KC":  1972,  # GEHA Field at Arrowhead Stadium
    "LAC": 2020,  # SoFi Stadium
    "LAR": 2020,  # SoFi Stadium
    "LV":  2020,  # Allegiant Stadium
    "MIA": 1987,  # Hard Rock Stadium
    "MIN": 2016,  # U.S. Bank Stadium
    "NE":  2002,  # Gillette Stadium
    "NO":  1975,  # Caesars Superdome
    "NYG": 2010,  # MetLife Stadium
    "NYJ": 2010,  # MetLife Stadium
    "PHI": 2003,  # Lincoln Financial Field
    "PIT": 2001,  # Acrisure Stadium
    "SEA": 2002,  # Lumen Field
    "SF":  2014,  # Levi's Stadium
    "TB":  1998,  # Raymond James Stadium
    "TEN": 1999,  # Nissan Stadium
    "WSH": 1997,  # Northwest Stadium
}

# Which league-stat categories to surface as player leaders on the detail page
LEADER_CATEGORIES = [
    "passingYards",
    "passingTouchdowns",
    "rushingYards",
    "receivingYards",
    "totalTackles",
    "sacks",
    "interceptions",
]


async def fetch_teams() -> list[dict]:
    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.get(TEAMS_URL)
        resp.raise_for_status()
        data = resp.json()

    teams = []
    for entry in data.get("sports", [{}])[0].get("leagues", [{}])[0].get("teams", []):
        team = entry.get("team", {})
        logos = team.get("logos", [])
        logo_url = logos[0].get("href", "") if logos else ""
        teams.append({
            "id": team.get("id"),
            "name": team.get("name"),
            "abbrev": team.get("abbreviation"),
            "city": team.get("location"),
            "display_name": team.get("displayName"),
            "logo_url": logo_url,
        })
    return teams


async def fetch_standings() -> dict[str, dict]:
    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.get(STANDINGS_URL)
        resp.raise_for_status()
        data = resp.json()

    standings = {}
    for group in data.get("children", []):
        for entry in group.get("standings", {}).get("entries", []):
            team_id = entry.get("team", {}).get("id")
            stats = {s["name"]: s.get("value", 0) for s in entry.get("stats", []) if "name" in s}
            wins = int(stats.get("wins", 0))
            losses = int(stats.get("losses", 0))
            ties = int(stats.get("ties", 0))
            total = wins + losses + ties
            win_pct = (wins / total * 100) if total > 0 else 0.0
            standings[team_id] = {
                "wins": wins,
                "losses": losses,
                "ties": ties,
                "win_pct": round(win_pct, 1),
            }
    return standings


async def get_all_teams() -> list[dict]:
    teams = await fetch_teams()
    standings = await fetch_standings()

    merged = []
    for team in teams:
        record = standings.get(team["id"], {"wins": 0, "losses": 0, "ties": 0, "win_pct": 0.0})
        merged.append({**team, **record})

    merged.sort(key=lambda t: t["display_name"])
    return merged


async def fetch_team_detail(team_id: str) -> dict:
    """Fetch full team detail: info, venue, season stats, and player leaders."""
    async with httpx.AsyncClient(timeout=10) as client:
        team_resp, stats_resp, roster_resp, league_stats_resp = await asyncio.gather(
            client.get(f"{TEAMS_URL}/{team_id}"),
            client.get(f"{TEAMS_URL}/{team_id}/statistics"),
            client.get(f"{TEAMS_URL}/{team_id}/roster"),
            client.get(LEAGUE_STATS_URL),
        )
        team_resp.raise_for_status()
        stats_resp.raise_for_status()

    # ── Team info & venue ─────────────────────────────────────
    team = team_resp.json()["team"]
    franchise = team.get("franchise", {})
    venue = franchise.get("venue", {})
    logos = team.get("logos", [])
    logo_url = logos[0].get("href", "") if logos else ""
    abbrev = team.get("abbreviation", "")

    info = {
        "id": team.get("id"),
        "display_name": team.get("displayName"),
        "name": team.get("name"),
        "city": team.get("location"),
        "abbrev": abbrev,
        "color": team.get("color", "013369"),
        "alt_color": team.get("alternateColor", "d50a0a"),
        "logo_url": logo_url,
        "venue_name": venue.get("fullName", ""),
        "venue_city": venue.get("address", {}).get("city", ""),
        "venue_state": venue.get("address", {}).get("state", ""),
        "venue_opened": STADIUM_OPENED.get(abbrev),
        "venue_surface": "Grass" if venue.get("grass") else "Turf",
        "venue_indoor": venue.get("indoor", False),
    }

    # ── Team season stats ─────────────────────────────────────
    stats_data = stats_resp.json()
    categories = stats_data.get("results", {}).get("stats", {}).get("categories", [])
    stat_map: dict[str, dict] = {}
    for cat in categories:
        for s in cat.get("stats", []):
            stat_map[s["name"]] = s

    def sv(name: str) -> str:
        return stat_map.get(name, {}).get("displayValue", "—")

    team_stats = {
        "offense": [
            {"label": "Points Per Game",         "value": sv("totalPointsPerGame")},
            {"label": "Total Points",             "value": sv("totalPoints")},
            {"label": "Pass Yards/Game",          "value": sv("netPassingYardsPerGame")},
            {"label": "Rush Yards/Game",          "value": sv("rushingYardsPerGame")},
            {"label": "Total Yards/Game",         "value": sv("yardsPerGame")},
            {"label": "Passing TDs",              "value": sv("passingTouchdowns")},
            {"label": "Rushing TDs",              "value": sv("rushingTouchdowns")},
            {"label": "Completion %",             "value": sv("completionPct") + "%"},
            {"label": "Interceptions Thrown",     "value": sv("interceptions")},
            {"label": "QB Rating",                "value": sv("QBRating")},
            {"label": "Sacks Allowed",            "value": sv("sacks")},
            {"label": "3rd Down %",               "value": sv("thirdDownConvPct") + "%"},
        ],
        "defense": [
            {"label": "Sacks",                   "value": sv("sacks")},
            {"label": "Total Tackles",            "value": sv("totalTackles")},
            {"label": "Tackles For Loss",         "value": sv("tacklesForLoss")},
            {"label": "Passes Defended",          "value": sv("passesDefended")},
            {"label": "Interceptions",            "value": sv("avgInterceptionYards")},
        ],
    }

    # ── Player leaders (filtered from league-wide stats) ──────
    player_leaders: list[dict] = []
    if league_stats_resp.is_success:
        league_data = league_stats_resp.json()
        for cat in league_data.get("stats", {}).get("categories", []):
            if cat["name"] not in LEADER_CATEGORIES:
                continue
            for entry in cat.get("leaders", []):
                if entry.get("team", {}).get("id") == team_id:
                    athlete = entry.get("athlete", {})
                    headshot = athlete.get("headshot", {})
                    player_leaders.append({
                        "category": cat["displayName"],
                        "player_name": athlete.get("displayName", ""),
                        "value": entry.get("displayValue", ""),
                        "headshot_url": headshot.get("href", "") if isinstance(headshot, dict) else "",
                    })
                    break  # only top player per category for this team

    # ── Roster grouped by unit ────────────────────────────────
    roster: list[dict] = []
    if roster_resp.is_success:
        for group in roster_resp.json().get("athletes", []):
            unit = group.get("position", "").capitalize()
            for p in group.get("items", []):
                headshot = p.get("headshot", {})
                roster.append({
                    "unit": unit,
                    "name": p.get("displayName", ""),
                    "position": p.get("position", {}).get("displayName", ""),
                    "jersey": p.get("jersey") or "—",
                    "headshot_url": headshot.get("href", "") if isinstance(headshot, dict) else "",
                })

    return {**info, "team_stats": team_stats, "player_leaders": player_leaders, "roster": roster}
