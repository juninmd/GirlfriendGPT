from typing import Optional
from langchain_core.tools import tool
from src.config import Config
# Import ElevenLabs only if available/configured to avoid crash if not needed immediately
try:
    from elevenlabs.client import ElevenLabs
    from elevenlabs import play
except ImportError:
    ElevenLabs = None

@tool
def generate_selfie(description: str) -> str:
    """
    Generates a selfie based on the description.
    Use this tool when the user asks for a photo, selfie, or image of you.
    The description should describe the scene and your appearance.
    """
    # Placeholder for actual image generation
    # In a real "2026" scenario, this would call Gemini Pro Vision or Imagen 3 API
    return f"[IMAGE: Selfie of me doing {description}]"

@tool
def generate_voice_message(text: str) -> str:
    """
    Generates a voice message (audio) of you speaking the text.
    Use this tool when the user asks for a voice note or audio message.
    """
    if not Config.ELEVENLABS_API_KEY:
        return "[Voice message cannot be generated: Missing API Key]"

    # Placeholder for actual voice generation logic
    # We would use ElevenLabs SDK here
    return f"[AUDIO: Voice message saying '{text}']"

def get_tools():
    return [generate_selfie, generate_voice_message]
