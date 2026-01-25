import os
import sys
import unittest
from unittest.mock import MagicMock, patch

from langchain_core.messages import HumanMessage, SystemMessage

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.agent import create_agent
from src.config import Config, Personality


class TestAgentPrompt(unittest.TestCase):
    def setUp(self):
        self.personality = Personality(
            name="FutureBot",
            byline="A bot from the future",
            identity=["I am a future bot"],
            behavior=["I predict things"],
            profile_image=None,
        )

    @patch("src.agent.ChatGoogleGenerativeAI")
    def test_system_prompt_contains_2026(self, mock_llm_class):
        # Mock the LLM instance
        mock_llm_instance = MagicMock()
        mock_llm_class.return_value = mock_llm_instance

        # Mock bind_tools to return the same instance (or another mock)
        mock_llm_with_tools = MagicMock()
        mock_llm_instance.bind_tools.return_value = mock_llm_with_tools

        # Setup the invoke return value to avoid errors
        mock_llm_with_tools.invoke.return_value = SystemMessage(content="Response")

        # Create the agent
        with patch.object(Config, "GOOGLE_API_KEY", "fake_key"):
            app = create_agent(self.personality)

        # Invoke the agent
        input_message = HumanMessage(content="Hello")
        app.invoke(
            {"messages": [input_message]},
            config={"configurable": {"thread_id": "test"}},
        )

        # Verify that invoke was called on the LLM
        # The arguments to invoke should be a list of messages
        # The first message should be the SystemMessage

        # Get the arguments of the call
        args, kwargs = mock_llm_with_tools.invoke.call_args
        messages = args[0]

        # Check first message
        self.assertIsInstance(messages[0], SystemMessage)
        self.assertIn("The current year is 2026", messages[0].content)
        self.assertIn("FutureBot", messages[0].content)


if __name__ == "__main__":
    unittest.main()
