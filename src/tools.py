from typing import Optional
from langchain_core.tools import tool
from src.config import Config
import logging

# Import ElevenLabs only if available/configured to avoid crash if not needed immediately
try:
    from elevenlabs.client import ElevenLabs
    from elevenlabs import save
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
    # Since we don't have an image generation API key in the env, we mock it.
    return f"[IMAGE_PLACEHOLDER: A selfie of me {description}]"

@tool
def generate_voice_message(text: str) -> str:
    """
    Generates a voice message (audio) of you speaking the text.
    Use this tool when the user asks for a voice note or audio message.
    """
    if not Config.ELEVENLABS_API_KEY:
        return "[Voice message cannot be generated: Missing ELEVENLABS_API_KEY]"

    if not ElevenLabs:
        return "[Voice message cannot be generated: ElevenLabs library not installed]"

    try:
        client = ElevenLabs(api_key=Config.ELEVENLABS_API_KEY)
        # Using a default voice ID (Rachel is a common default in ElevenLabs examples)
        # In a real app, this should be configurable per personality
        voice_id = "21m00Tcm4TlvDq8ikWAM" # Rachel

        audio = client.generate(
            text=text,
            voice=voice_id,
            model="eleven_monolingual_v1"
        )

        # In a real bot, we would save this to a file and return the path or bytes.
        # For this tool, returning a path or a success message is appropriate.
        # Since we can't easily return bytes to the LLM, we return a sentinel string
        # that the Telegram bot can parse, or just a description.

        # However, the Agent logic just gets the string back.
        # The Telegram bot would need to handle this.
        # For now, to satisfy the requirement of "Functionality", I will simulate saving it.

        filename = "voice_message.mp3"
        save(audio, filename)

        return f"[AUDIO_FILE: {filename}]"

    except Exception as e:
        logging.error(f"Error generating voice: {e}")
        return f"[Error generating voice message: {str(e)}]"

def get_tools():
    return [generate_selfie, generate_voice_message]
