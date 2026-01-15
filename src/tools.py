import os
import requests
from typing import Optional, Type
from langchain_core.tools import BaseTool
from pydantic import BaseModel, Field
from src.config import Config

class SelfieToolInput(BaseModel):
    description: str = Field(description="A description of the selfie to generate.")

class SelfieTool(BaseTool):
    name: str = "SelfieTool"
    description: str = "Generates a selfie based on the description. Use this when the user asks for a photo or selfie."
    args_schema: Type[BaseModel] = SelfieToolInput

    def _run(self, description: str) -> str:
        # Placeholder implementation
        # In a real 2026 scenario, this would call Gemini's image generation or another API.
        print(f"[SelfieTool] Generating selfie for: {description}")
        return f"I've snapped a selfie for you! (Imagine a photo of me: {description})"

    async def _arun(self, description: str) -> str:
        # Async implementation
        return self._run(description)

class VoiceToolInput(BaseModel):
    text: str = Field(description="The text to speak.")

class VoiceTool(BaseTool):
    name: str = "VoiceTool"
    description: str = "Generates spoken audio from text. Use this to send a voice message."
    args_schema: Type[BaseModel] = VoiceToolInput

    def _run(self, text: str) -> str:
        if not Config.ELEVENLABS_API_KEY:
            return "Voice generation is not configured (missing API key)."

        url = f"https://api.elevenlabs.io/v1/text-to-speech/{Config.ELEVENLABS_VOICE_ID}"
        headers = {
            "Accept": "audio/mpeg",
            "Content-Type": "application/json",
            "xi-api-key": Config.ELEVENLABS_API_KEY
        }
        data = {
            "text": text,
            "model_id": "eleven_monolingual_v1",
            "voice_settings": {
                "stability": 0.5,
                "similarity_boost": 0.5
            }
        }

        try:
            response = requests.post(url, json=data, headers=headers)
            if response.status_code == 200:
                # In a real app, we would save the audio and return a path or URL.
                # For now, let's assume we save it to a temp file or return a success message.
                # Since this is a tool usage, we return a string indicating success.
                # The actual audio handling would need to be done by the bot (sending the file).
                # But tools usually return text to the LLM.
                # Maybe the tool should return "Audio generated at <path>".
                # Let's save to a temporary file.
                import tempfile
                with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as f:
                    f.write(response.content)
                    return f"AUDIO_GENERATED:{f.name}"
            else:
                return f"Error generating voice: {response.text}"
        except Exception as e:
            return f"Exception during voice generation: {str(e)}"

    async def _arun(self, text: str) -> str:
        return self._run(text)
