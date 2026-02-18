import httpx

TEAMS_URL = "https://site.api.espn.com/apis/site/v2/sports/football/nfl/teams"
STANDINGS_URL = "https://site.api.espn.com/apis/v2/sports/football/nfl/standings"


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
            stats = {s["name"]: s["value"] for s in entry.get("stats", [])}
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
