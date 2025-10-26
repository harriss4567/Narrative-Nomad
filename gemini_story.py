import google.generativeai as genai
from pydantic import BaseModel, Field
from dotenv import load_dotenv
import os
import json
from typing import List, Optional
from fastapi import HTTPException

# Load environment variables from .env file
load_dotenv()

# Initialize the Gemini client with API key from environment variable
api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    raise ValueError("GOOGLE_API_KEY not found in environment variables. Make sure you have a .env file with the API key.")
print("API Key loaded successfully (first 4 chars):", api_key[:4] if api_key else "None")
genai.configure(api_key=api_key)

# Set default generation config
generation_config = {
    "temperature": 0.9,
    "top_p": 1,
    "top_k": 1,
    "max_output_tokens": 2048,
}

class GeoLocation(BaseModel):
    lat: float
    lng: float

class Place(BaseModel):
    name: str
    address: Optional[str] = None
    geo: Optional[GeoLocation] = None
    url: Optional[str] = None
    price_estimate: Optional[str] = None # e.g., "$$", "€€€"
    description: Optional[str] = None
    menu_items: Optional[List[str]] = None # For restaurants

class Activity(BaseModel):
    type: str # e.g., "Sightseeing", "Dining", "Hiking", "Museum Visit", "Shopping"
    description: str
    estimated_price_usd: Optional[float] = None
    time_allocation: Optional[str] = None # e.g., "2-3 hours", "Morning", "Evening"
    places: Optional[List[Place]] = None

class Chapter(BaseModel):
    day: int
    title: str
    time_window: str # e.g., "Morning", "Afternoon", "Evening"
    story_paragraph: str
    activities: List[Activity]
    story_image_prompt: str # A descriptive prompt for image generation related to this chapter

class TripPlanSchema(BaseModel):
    title: str
    summary: str
    destination: str
    travel_style: str
    chapters: List[Chapter]

# Define a GeminiClient class to encapsulate interaction with the Gemini API
class GeminiClient:
    def __init__(self):
        # We'll keep this as gemini-pro for now, but the list_available_models will help confirm
        self.model = genai.GenerativeModel('gemini-pro') 
    
    def list_available_models(self):
        """Lists all models accessible with the current API key."""
        print("\n--- Listing available Gemini models ---")
        try:
            for m in genai.list_models():
                # Filter to only show 'generateContent' capable models, as that's what we need
                if "generateContent" in m.supported_generation_methods:
                    print(f"Model: {m.name}, Supported methods: {m.supported_generation_methods}")
        except Exception as e:
            print(f"Error listing models: {e}")
        print("--------------------------------------\n")


    def generate_structured_itinerary(self, origin: str, destination: str, duration_days: int, budget: float, travel_style: str, interests: List[str], eat_out: bool) -> dict:
        interests_str = ", ".join(interests) if interests else "no specific interests"
        eat_out_pref = "The user wants recommendations for places to eat out, including specific restaurant names, addresses, and a brief description of their offerings/menu items. Integrate these into the daily activities." if eat_out else "The user prefers not to have specific eating out recommendations."

        # Crafting a very detailed prompt to guide Gemini
        prompt = f"""
        You are an expert travel planner and a master storyteller. Your task is to create a detailed, day-by-day travel itinerary and an engaging narrative for a trip, tailored to the user's preferences.

        Here are the trip details:
        - Origin: {origin}
        - Destination: {destination}
        - Duration: {duration_days} days
        - Budget: ${budget:.2f} (USD) - This is a total budget for activities, food, and local travel. Please provide estimated prices where possible.
        - Travel Style/Story Theme: {travel_style} - The entire story, activities, and recommendations should align with this theme.
        - Interests: {interests_str}
        - Eating Out Preference: {eat_out_pref}

        Your output MUST be a JSON object that strictly adheres to the provided Pydantic schema `TripPlanSchema`.
        Ensure the following for each chapter (day):

        1.  **Story Integration**: Each day (chapter) must have a `story_paragraph` that advances the narrative, fitting the chosen `{travel_style}` theme. The story should be immersive and descriptive.
        2.  **Detailed Activities**: For each `activity`, provide a clear `type`, a detailed `description`, an `estimated_price_usd`, and a `time_allocation` (e.g., "Morning", "2-3 hours").
        3.  **Specific Places**: For `places` within an activity, provide:
            *   `name`: The exact name of the venue/attraction.
            *   `address`: A specific address if possible (street, city, country).
            *   `geo`: Latitude and longitude. Try to find these for prominent locations. If you cannot find exact coordinates, you can use general ones for the city, but aim for specificity.
            *   `url`: A link to the official website or a reputable review site (e.g., Google Maps link, official tourism site).
            *   `price_estimate`: A price range (e.g., "$", "$$", "$$$").
            *   `description`: A brief description of the place.
            *   `menu_items`: If `eat_out` is true and it's a restaurant, suggest 2-3 specific popular or thematic menu items.
        4.  **Plot Development**: The story should have a clear beginning, middle, and end over the duration of the trip, with a coherent plot that evolves each day.
        5.  **Image Prompts**: For each chapter, include a `story_image_prompt` that describes a visual scene from the `story_paragraph`. This prompt will be used for image generation, so make it descriptive and thematic.
        6.  **Budget Adherence**: Ensure the suggested activities and dining options are reasonable within the overall budget.
        7.  **Real-world Accuracy**: Provide real, actionable locations, restaurants, and attractions. Avoid generic suggestions.

        Example (abbreviated for clarity, actual output should be comprehensive):
        ```json
        {{
          "title": "A Romantic Escapade in Paris",
          "summary": "Embark on a fairytale journey through the City of Love, filled with charming cafes, iconic landmarks, and intimate moments.",
          "destination": "Paris",
          "travel_style": "romantic",
          "chapters": [
            {{
              "day": 1,
              "title": "Arrival and Parisian Embrace",
              "time_window": "Afternoon & Evening",
              "story_paragraph": "The moment you stepped off the train, a crisp autumn breeze carrying the scent of fresh croissants and old stone buildings welcomed you to Paris. Hand in hand, you wandered through the charming streets of Le Marais, the golden hour light casting a magical glow over every corner. This was it, the beginning of your romantic adventure.",
              "activities": [
                {{
                  "type": "Arrival & Check-in",
                  "description": "Arrive at your accommodation, settle in, and prepare for your Parisian adventure.",
                  "estimated_price_usd": 0.0,
                  "time_allocation": "2 hours",
                  "places": []
                }},
                {{
                  "type": "Romantic Stroll & Dinner",
                  "description": "Explore the historic Le Marais district, known for its beautiful architecture and vibrant atmosphere. Enjoy a romantic dinner at a classic Parisian bistro.",
                  "estimated_price_usd": 80.0,
                  "time_allocation": "3-4 hours",
                  "places": [
                    {{
                      "name": "Le Marais",
                      "address": "Le Marais, Paris, France",
                      "geo": {{"lat": 48.8596, "lng": 2.3610}},
                      "url": "https://en.parisinfo.com/neighbourhoods-paris/le-marais",
                      "description": "A historic district in Paris, known for its well-preserved architecture, narrow streets, and chic boutiques.",
                      "price_estimate": ""
                    }},
                    {{
                      "name": "Le Petit Marché",
                      "address": "9 Rue de Béarn, 75003 Paris, France",
                      "geo": {{"lat": 48.8569, "lng": 2.3644}},
                      "url": "https://www.lepetitmarche.fr/",
                      "price_estimate": "$$",
                      "description": "A cozy, authentic Parisian bistro offering classic French dishes with a modern twist. Known for its intimate atmosphere.",
                      "menu_items": ["Duck Confit", "Steak Frites", "Crème Brûlée"]
                    }}
                  ]
                }}
              ],
              "story_image_prompt": "A couple holding hands, walking through the narrow, cobbled streets of Le Marais in Paris at golden hour, with historic buildings and charming streetlights around them."
            }}
          ]
        }}
        ```
        """
        
        generation_config = {
            "temperature": 0.9,  # Higher temperature for more creative stories
            "max_output_tokens": 3000,  # Increased token limit for detailed output
        }

        response = None
        try:
            response = self.model.generate_content(
                contents=[prompt],
                generation_config=generation_config,
                safety_settings=[
                    {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
                    {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
                    {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
                    {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
                ]
            )
            
            if not response or not response.text:
                raise Exception("Empty response from Gemini API")
                
            # Validate and parse the JSON
            try:
                plan_data = json.loads(response.text)
                TripPlanSchema(**plan_data)  # Validate against schema
                return plan_data
            except json.JSONDecodeError as je:
                raise Exception(f"Invalid JSON response: {je}. Response text: {response.text[:200]}...")
            except Exception as ve:
                raise Exception(f"Schema validation error: {ve}. Response text: {response.text[:200]}...")
                
        except Exception as e:
            error_msg = f"Error generating itinerary: {str(e)}"
            if response and hasattr(response, 'candidates') and response.candidates:
                error_msg += f"\nResponse parts: {response.candidates[0].content.parts}"
            print(error_msg)
            raise HTTPException(status_code=500, detail=error_msg)