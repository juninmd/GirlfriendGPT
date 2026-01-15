import os
import json
from typing import List, Optional
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
    ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")

    # Default personality
    DEFAULT_PERSONALITY = "luna"

    @staticmethod
    def load_personality(name: str) -> Personality:
        try:
            # Try loading from src/personalities
            path = os.path.join("src", "personalities", f"{name}.json")
            with open(path, "r") as f:
                data = json.load(f)
                return Personality(**data)
        except FileNotFoundError:
            # Fallback or error
            print(f"Personality {name} not found. Loading default.")
            if name != Config.DEFAULT_PERSONALITY:
                return Config.load_personality(Config.DEFAULT_PERSONALITY)
            raise ValueError(f"Default personality {name} not found!")

    @staticmethod
    def validate():
        if not Config.GOOGLE_API_KEY:
            print("Warning: GOOGLE_API_KEY is not set. The bot brain will not work.")
        if not Config.TELEGRAM_TOKEN:
            print("Warning: TELEGRAM_TOKEN is not set. Telegram bot will not work.")

if __name__ == "__main__":
    Config.validate()
    p = Config.load_personality("luna")
    print(f"Loaded personality: {p.name}")
