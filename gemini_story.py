from google import genai
from google.genai import types
from pydantic import BaseModel
from dotenv import load_dotenv
import os
import json

# Load environment variables from .env file
load_dotenv()

# Initialize the Gemini client with API key from environment variable
client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))

# Define a schema for the trip plan response
class TripPlanSchema(BaseModel):
    day: int
    activities: list
    meals: list
    travel_costs: float
    locations: list
    story_element: str

# Define a GeminiClient class to encapsulate interaction with the Gemini API
class GeminiClient:
    def __init__(self):
        self.client = client
    
    # Method to generate a structured itinerary based on the provided prompt
    def generate_structured_itinerary(self, prompt: str) -> dict:

        response = self.client.generate(
            model="gemini-2.5-flash",
            contents=prompt,
            temperature=0.7,
            max_output_tokens=1500,
            config = types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=TripPlanSchema,
        ),
    )
        return json.loads(response.text)
        
        
        