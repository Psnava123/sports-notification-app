import os
import requests
from fastapi import FastAPI, BackgroundTasks
import nest_asyncio
import uvicorn
from datetime import datetime
from pushbullet import Pushbullet
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

# Initialize FastAPI
app = FastAPI()

# API Keys
CRICKET_API_KEY = os.getenv("CRICKET_API_KEY", "b010864b-f0c8-414f-aebd-08f7996a1e69")
FOOTBALL_API_KEY = os.getenv("FOOTBALL_API_KEY", "c9751a3f6f4a4e7c9cd0721a71d6cd53")
PUSHBULLET_API_KEY = os.getenv("PUSHBULLET_API_KEY", "o.DV1U6GIbuhS3wrVhU82IywCrqmZyW2kD")

# Pushbullet instance
pb = Pushbullet(PUSHBULLET_API_KEY)

# API URLs
CRICKET_API_URL = f"https://api.cricapi.com/v1/currentMatches?apikey={CRICKET_API_KEY}"
FOOTBALL_API_URL = "https://api.football-data.org/v4/matches"
FOOTBALL_API_HEADERS = {"X-Auth-Token": FOOTBALL_API_KEY}

# Function to send notifications
def send_notification(title, message):
    pb.push_note(title, message)

# Fetch cricket matches
def get_cricket_matches():
    response = requests.get(CRICKET_API_URL)
    if response.status_code != 200:
        return {"error": "Failed to fetch Cricket API"}

    today = datetime.now().strftime('%Y-%m-%d')
    matches = response.json().get("data", [])
    upcoming_matches = [m for m in matches if m.get("date") >= today]

    if upcoming_matches:
        message = "\n".join([f"{m['name']} on {m['date']}" for m in upcoming_matches])
        send_notification("Upcoming Cricket Matches", message)
        return upcoming_matches
    return {"message": "No upcoming matches."}

# Fetch football matches
def get_football_matches():
    response = requests.get(FOOTBALL_API_URL, headers=FOOTBALL_API_HEADERS)
    if response.status_code != 200:
        return {"error": "Failed to fetch Football API"}

    matches = response.json().get("matches", [])
    upcoming_matches = [m for m in matches if m.get("status") == "SCHEDULED"]

    if upcoming_matches:
        message = "\n".join([f"{m['homeTeam']['name']} vs {m['awayTeam']['name']} on {m['utcDate']}" for m in upcoming_matches])
        send_notification("Upcoming Football Matches", message)
        return upcoming_matches
    return {"message": "No upcoming matches."}

# Schedule periodic task
def schedule_task():
    scheduler = BackgroundScheduler()
    scheduler.add_job(get_cricket_matches, IntervalTrigger(hours=1), id='cricket_task')
    scheduler.add_job(get_football_matches, IntervalTrigger(hours=1), id='football_task')
    scheduler.start()

# Startup event
@app.on_event("startup")
async def on_startup():
    schedule_task()

# Shutdown event
@app.on_event("shutdown")
async def on_shutdown():
    # You can add shutdown tasks here if necessary
    pass

# Serve homepage (index.html)
@app.get("/")
async def home():
    frontend_path = "./frontend/index.html"
    if os.path.exists(frontend_path):
        with open(frontend_path, "r") as file:
            return HTMLResponse(file.read())
    else:
        return {"error": "index.html not found"}

# Mount frontend static files (e.g., CSS, JS) for serving
app.mount("/frontend", StaticFiles(directory="./frontend"), name="frontend")

# API Endpoints
@app.get("/matches/cricket")
def cricket_endpoint(background_tasks: BackgroundTasks):
    background_tasks.add_task(get_cricket_matches)
    return {"message": "Checking for upcoming cricket matches."}

@app.get("/matches/football")
def football_endpoint(background_tasks: BackgroundTasks):
    background_tasks.add_task(get_football_matches)
    return {"message": "Checking for upcoming football matches."}

# Allow FastAPI in Jupyter
nest_asyncio.apply()

# Run server
if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)