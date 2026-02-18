from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from espn import get_all_teams, fetch_team_detail

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    teams = await get_all_teams()
    return templates.TemplateResponse("index.html", {"request": request, "teams": teams})


@app.get("/team/{team_id}", response_class=HTMLResponse)
async def team_detail(request: Request, team_id: str):
    team = await fetch_team_detail(team_id)
    return templates.TemplateResponse("team.html", {"request": request, "team": team})
