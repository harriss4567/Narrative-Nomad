from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
from gemini_story import GeminiClient
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse, StreamingResponse
from pathlib import Path
from eleven_labs_audio import generate_narration 

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

@app.get("/api/chapter/{chapter_idx}/audio")
async def chapter_audio(chapter_idx: int, text: str = ""):
    if not text:
        raise HTTPException(status_code=400, detail="No text provided for narration")

    try:
        audio_bytes = generate_narration(text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"ElevenLabs error: {e}")

    # Return audio to frontend
    return StreamingResponse(audio_bytes, media_type="audio/mpeg")