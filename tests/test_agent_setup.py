import unittest
from unittest.mock import patch, MagicMock
import sys
import os

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.config import Personality, Config
from src.agent import create_agent, tools


class TestAgentSetup(unittest.TestCase):
    def setUp(self):
        self.personality = Personality(
            name="TestBot",
            byline="A test bot",
            identity=["I am a test bot"],
            behavior=["I behave nicely"],
            profile_image=None,
        )

    @patch("src.agent.ChatGoogleGenerativeAI")
    def test_agent_creation_with_gemini(self, mock_llm):
        # Mock the LLM to avoid API calls and key errors
        mock_instance = MagicMock()
        mock_llm.return_value = mock_instance
        # Mock bind_tools
        mock_instance.bind_tools.return_value = mock_instance

        # Mock Config to ensure we don't fail on missing env vars if checked early
        with patch.object(Config, "GOOGLE_API_KEY", "fake_key"):
            app = create_agent(self.personality)

        # Verify LLM was initialized with correct model
        mock_llm.assert_called_with(
            model="gemini-2.5-pro",
            api_key="fake_key",
            temperature=0.8,
            max_tokens=None,
            timeout=None,
            max_retries=2,
        )

        # Verify tools are bound
        mock_instance.bind_tools.assert_called_with(tools)

        # Verify app is created (it should be a compiled graph)
        self.assertIsNotNone(app)

    def test_tools_configuration(self):
        # Check if we have the expected tools
        tool_names = [t.name for t in tools]
        self.assertIn("SelfieTool", tool_names)
        self.assertIn("VoiceTool", tool_names)


if __name__ == "__main__":
    unittest.main()
