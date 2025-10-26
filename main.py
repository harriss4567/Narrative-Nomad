from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
from gemini_story import GeminiClient
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from pathlib import Path

app = FastAPI()
client = GeminiClient()

# Serve static files (HTML, CSS, JS, etc.)
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
async def root():
    # Serve your index.html
    path = Path("static/index.html")
    return HTMLResponse(path.read_text())


class TripRequest(BaseModel):
    origin: str
    destination: str
    duration_days: int
    budget: float
    travel_style: str
    interests: list[str]
    eat_out: bool

@app.post("/api/plan")
async def create_plan(request: TripRequest):
    # TODO: generate a trip plan here
    return {
        "title": f"Trip to {request.destination}",
        "summary": f"A {request.travel_style} trip from {request.origin} to {request.destination}.",
        "destination": request.destination,
        "chapters": []
    }