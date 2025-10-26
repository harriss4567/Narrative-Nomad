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

#TODO: Connect the text of the generated story into here
#      Put winget install Gyan.FFmpeg as a requirement
# Creates the audio for the inputed text using the model with model_id and voice with voice_id into
# format output_format
audio = elevenlabs.text_to_speech.convert(
    text="The first move is what sets everything in motion.",
    voice_id=voice_id1,
    model_id=model_id1,
    output_format="mp3_44100_128",
)

# Plays the audio
play(audio)
