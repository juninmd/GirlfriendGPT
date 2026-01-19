import unittest
from unittest.mock import patch, MagicMock
import sys
import os

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.config import Personality, Config
from src.agent import create_agent, tools

class TestAgentOllama(unittest.TestCase):
    def setUp(self):
        self.personality = Personality(
            name="TestBot",
            byline="A test bot",
            identity=["I am a test bot"],
            behavior=["I behave nicely"],
            profile_image=None
        )

    @patch("src.agent.ChatOllama")
    def test_agent_creation_with_ollama(self, mock_llm):
        # Mock the LLM to avoid API calls
        mock_instance = MagicMock()
        mock_llm.return_value = mock_instance
        # Mock bind_tools
        mock_instance.bind_tools.return_value = mock_instance

        # Mock Config to use ollama
        with patch.object(Config, 'LLM_PROVIDER', 'ollama'), \
             patch.object(Config, 'OLLAMA_MODEL', 'llama3-test'):
             app = create_agent(self.personality)

        # Verify LLM was initialized with correct model
        mock_llm.assert_called_with(
            model="llama3-test",
            base_url=Config.OLLAMA_BASE_URL,
            temperature=0.8,
        )

        # Verify tools are bound
        mock_instance.bind_tools.assert_called_with(tools)

        # Verify app is created
        self.assertIsNotNone(app)

    @patch("src.agent.ChatGoogleGenerativeAI")
    def test_agent_creation_with_gemini_2_5(self, mock_llm):
        # Mock the LLM
        mock_instance = MagicMock()
        mock_llm.return_value = mock_instance
        mock_instance.bind_tools.return_value = mock_instance

        # Mock Config to use google (default)
        with patch.object(Config, 'LLM_PROVIDER', 'google'), \
             patch.object(Config, 'GOOGLE_API_KEY', 'fake_key'):
             app = create_agent(self.personality)

        # Verify LLM was initialized with gemini-2.5-pro
        mock_llm.assert_called_with(
            model="gemini-2.5-pro",
            api_key='fake_key',
            temperature=0.8,
            max_tokens=None,
            timeout=None,
            max_retries=2,
        )

if __name__ == '__main__':
    unittest.main()
