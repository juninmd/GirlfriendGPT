import json
import os
from pathlib import Path
from typing import Dict, List, Optional

from dotenv import load_dotenv
from pydantic import BaseModel

# Load environment variables
load_dotenv()


class Personality(BaseModel):
    name: str
    byline: str
    identity: List[str]
    behavior: List[str]
    profile_image: Optional[str] = None


class Config:
    TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
    EDGE_TTS_VOICE = os.getenv("EDGE_TTS_VOICE", "en-US-AriaNeural")

    # New configuration for LLM provider
    LLM_PROVIDER = os.getenv("LLM_PROVIDER", "google")  # 'google' or 'ollama'
    GOOGLE_MODEL = os.getenv("GOOGLE_MODEL", "gemini-3.0-pro")  # 2026 Default (Gemini)
    OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3")  # Default model for Ollama

    CURRENT_YEAR = 2026

    @staticmethod
    def load_personalities(
        personalities_dir: str = "src/personalities",
    ) -> Dict[str, Personality]:
        personalities: Dict[str, Personality] = {}
        path = Path(personalities_dir)
        if not path.exists():
            return personalities

        for file_path in path.glob("*.json"):
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    personality = Personality(**data)
                    personalities[personality.name.lower()] = personality
            except Exception as e:
                print(f"Error loading personality from {file_path}: {e}")

        return personalities

    @staticmethod
    def validate() -> None:
        if Config.LLM_PROVIDER == "google" and not Config.GOOGLE_API_KEY:
            raise ValueError("GOOGLE_API_KEY environment variable is not set.")
        # Telegram token is optional for CLI mode, but generally required for the bot
