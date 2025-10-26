from dotenv import load_dotenv
from elevenlabs.client import ElevenLabs
from elevenlabs.play import play
import os

# Load environment variables from .env file
load_dotenv()

# Gets the api key for elevenlabs
elevenlabs = ElevenLabs(
  api_key=os.getenv("ELEVENLABS_API_KEY"),
)

# Gets the id of the model and voice used from elevenlabs
voice_id1 = os.getenv("VOICE_ID")
model_id1 = os.getenv("MODEL_ID")

# Creates the audio for the inputed text using the model with model_id and voice with voice_id into
# format output_format
def generate_narration(text: str):
    """
    Convert text -> MP3 audio bytes using ElevenLabs.
    Returns raw audio bytes, without playing them.
    """
    audio = elevenlabs.text_to_speech.convert(
        text=text,
        voice_id=voice_id1,
        model_id=model_id1,
        output_format="mp3_44100_128",
    )
    return audio