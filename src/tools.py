import os
import requests
import tempfile
from typing import Optional, Type
from langchain_core.tools import BaseTool
from pydantic import BaseModel, Field
from google import genai
from google.genai import types
from src.config import Config
import edge_tts
import asyncio

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
            # Use 'imagen-3.0-generate-001' for high fidelity "2026" results.
            response = client.models.generate_images(
                model='imagen-3.0-generate-001',
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

    async def _arun(self, text: str) -> str:
        if not Config.EDGE_TTS_VOICE:
            return "Voice generation is not configured (missing EDGE_TTS_VOICE)."

        print(f"[VoiceTool] Generating voice for: {text}")

        try:
            communicate = edge_tts.Communicate(text, Config.EDGE_TTS_VOICE)
            with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as f:
                temp_filename = f.name
            
            # edge-tts save is async
            await communicate.save(temp_filename)
            return f"AUDIO_GENERATED:{temp_filename}"

        except Exception as e:
            return f"Error generating voice: {str(e)}"

    def _run(self, text: str) -> str:
        # Fallback for sync execution, though not recommended in async app
        try:
             return asyncio.run(self._arun(text))
        except RuntimeError:
             # If loop is already running, we can't use asyncio.run. 
             # Refactoring to full async architecture is best, but for now:
             return "Error: Async event loop already running, cannot call synchronous _run. Please ensure the agent uses ainvoke."
