import os
import requests
import tempfile
from typing import Optional, Type
from langchain_core.tools import BaseTool
from pydantic import BaseModel, Field
from google import genai
from google.genai import types
from src.config import Config

class SelfieToolInput(BaseModel):
    description: str = Field(description="A description of the selfie to generate.")

class SelfieTool(BaseTool):
    name: str = "SelfieTool"
    description: str = "Generates a selfie based on the description. Use this when the user asks for a photo or selfie."
    args_schema: Type[BaseModel] = SelfieToolInput

    def _run(self, description: str) -> str:
        if not Config.GOOGLE_API_KEY:
             return "Image generation is not configured (missing GOOGLE_API_KEY)."

        print(f"[SelfieTool] Generating selfie for: {description}")

        try:
            client = genai.Client(api_key=Config.GOOGLE_API_KEY)
            # Use 'imagen-4.0-generate-001' for high fidelity "2026" results.
            response = client.models.generate_images(
                model='imagen-4.0-generate-001',
                prompt=description,
                config=types.GenerateImagesConfig(
                    number_of_images=1,
                )
            )

            if response.generated_images:
                image_bytes = response.generated_images[0].image.image_bytes

                with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
                    f.write(image_bytes)
                    return f"IMAGE_GENERATED:{f.name}"
            else:
                 return "Failed to generate image (no images returned)."

        except Exception as e:
            return f"Error generating selfie: {str(e)}"

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
                # Save to a temporary file.
                with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as f:
                    f.write(response.content)
                    return f"AUDIO_GENERATED:{f.name}"
            else:
                return f"Error generating voice: {response.text}"
        except Exception as e:
            return f"Exception during voice generation: {str(e)}"

    async def _arun(self, text: str) -> str:
        return self._run(text)
