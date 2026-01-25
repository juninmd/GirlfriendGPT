# GirlfriendGPT (2026 Edition)

Your personal AI companion, updated for the modern era using **Google Gemini**, **LangGraph**, and **LangChain**.

## Features

* **Google Gemini Integration**: Powered by the latest Gemini models (Gemini 2.5 Pro) for smart and fast conversations.
* **Ollama Support**: Run locally with open-source models (Llama 3, Mistral, etc.) via Ollama.
* **Custom Voice**: Uses `edge-tts` for high-quality, free text-to-speech.
* **Telegram Bot**: Directly send and receive messages from your AI companion via Telegram.
* **CLI Mode**: Chat with your companion directly in your terminal.
* **Personality**: Customize the AI's personality via JSON files.
* **Selfies**: AI is capable of generating selfies using **Google Imagen 3**.

## Prerequisites

* Python 3.9+
* Google Gemini API Key
* (Optional) Telegram Bot Token
* (Optional) Ollama (for local inference)

## Installation

1. Clone the repository.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Set up environment variables. Create a `.env` file in the root directory:
   ```bash
   GOOGLE_API_KEY=your_gemini_key
   TELEGRAM_TOKEN=your_telegram_token
   # Optional: Configure voice (default: en-US-AriaNeural)
   EDGE_TTS_VOICE=en-US-AriaNeural

   # Optional: Use Ollama (default: google)
   # LLM_PROVIDER=ollama
   # OLLAMA_BASE_URL=http://localhost:11434
   # OLLAMA_MODEL=llama3
   ```

## Usage

### CLI Mode (Local Testing)
Chat with your companion in the terminal:
```bash
python main.py --cli
```
You will be prompted to select a personality.

### Telegram Bot
Run the Telegram bot:
```bash
python main.py
```
Send `/start` to your bot on Telegram to begin.

## Personalities

Personalities are defined in `src/personalities/`. To add a new personality:

1. Create a JSON file (e.g., `jane.json`) in `src/personalities/`.
2. Follow the structure of existing files:
   ```json
   {
     "name": "Jane",
     "byline": "Your adventurous friend",
     "identity": ["You are Jane...", "You love hiking..."],
     "behavior": ["You are cheerful...", "You use emojis..."],
     "profile_image": "optional/path.png"
   }
   ```

## Development

We strictly enforce code quality and test coverage.

### VS Code Dev Container

This project includes a `.devcontainer` configuration. Open the folder in VS Code and click "Reopen in Container" to get a pre-configured environment with all dependencies and tools installed.

### Running Checks Locally

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Linting & Formatting (Ruff)**:
   ```bash
   ruff check .
   ruff format --check .
   ```

3. **Type Checking (Mypy)**:
   ```bash
   mypy src/
   ```
   Note: We enforce strict typing.

4. **Security Check (Bandit)**:
   ```bash
   bandit -r src/
   ```

5. **Tests & Coverage**:
   ```bash
   pytest
   ```
   Coverage must be 100%. Configuration is in `pyproject.toml`.

## License
MIT
