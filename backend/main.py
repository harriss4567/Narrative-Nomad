# backend/main.py
from fastapi import FastAPI, HTTPException, Request, Response
from pydantic import BaseModel
from typing import List, Optional
import os
import json

from gemini_story import GeminiClient
from eleven_labs_audio import ElevenClient
from map import find_places_for_activity

app = FastAPI(title="TripStoryer")

# initialize clients (they read credentials from env)
gemini = GeminiClient()
eleven = ElevenClient()

class TripRequest(BaseModel):
    origin: str
    destination: str
    start_date: Optional[str] = None
    duration_days: int
    budget: float
    travel_style: str
    interests: List[str] = []
    eat_out: bool = True

@app.post("/api/plan")
async def plan_trip(req: TripRequest):
    prompt = build_gemini_prompt(req)
    try:
        plan_json = gemini.generate_structured_itinerary(prompt)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gemini error: {str(e)}")

    # Basic validation & ensure keys exist
    if not isinstance(plan_json, dict):
        raise HTTPException(status_code=500, detail="Invalid plan format from Gemini")

    # For each activity, add place lookups (placeholder)
    for chap in plan_json.get("chapters", []):
        for act in chap.get("activities", []):
            # cheap fallback if Gemini already supplied places
            if not act.get("places"):
                act["places"] = find_places_for_activity(act.get("type","general"), req.destination, act.get("when"))

    return plan_json

@app.get("/api/chapter/{chapter_id}/audio")
async def chapter_audio(chapter_id: int, request: Request):
    text = request.query_params.get("text")
    if not text:
        raise HTTPException(status_code=400, detail="Provide ?text=... query parameter")
    try:
        audio_bytes = eleven.text_to_speech(text, voice="alloy", fmt="mp3")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"ElevenLabs error: {str(e)}")

    return Response(content=audio_bytes, media_type="audio/mpeg")


def build_gemini_prompt(req: TripRequest) -> str:
    # Ask Gemini to return machine-readable JSON
    prompt = f"""
You are TripStoryer — produce a JSON itinerary + story. Output only valid JSON.

Keys:
- title (string)
- summary (string)
- destination (string)
- chapters (array). Each chapter:
  - id (int), day (int), title (string), time_window (string), story_paragraph (string)
  - activities (array). Each activity: id, type, description, duration_mins, estimated_price_usd, location_name, geo {{lat,lng}}, places (array of objects with name, address, url, price_estimate, geo)

User constraints:
destination: {req.destination}
duration_days: {req.duration_days}
budget_usd: {req.budget}
travel_style: {req.travel_style}
interests: {req.interests}
eat_out: {req.eat_out}

Please produce {req.duration_days} chapters (one per day). Keep JSON syntactically valid and machine-parseable.
"""
    return prompt
