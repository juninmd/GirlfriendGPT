from unittest.mock import MagicMock, patch

import pytest
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage

from src.agent import create_agent
from src.config import Config, Personality

# --- Tests for src/agent.py ---


@pytest.fixture
def mock_personality():
    return Personality(
        name="TestBot",
        byline="A test bot",
        identity=["I am a robot"],
        behavior=["Beep boop"],
    )


def test_create_agent_ollama(mock_personality):
    with patch.object(Config, "LLM_PROVIDER", "ollama"):
        with patch("src.agent.ChatOllama") as MockOllama:
            with patch("src.agent.StateGraph"):
                create_agent(mock_personality)
                MockOllama.assert_called_once()
                # We can check if args were passed correctly
                assert MockOllama.call_args[1]["model"] == Config.OLLAMA_MODEL


def test_create_agent_google(mock_personality):
    with patch.object(Config, "LLM_PROVIDER", "google"):
        with patch("src.agent.ChatGoogleGenerativeAI") as MockGoogle:
            with patch("src.agent.StateGraph"):
                create_agent(mock_personality)
                MockGoogle.assert_called_once()
                assert MockGoogle.call_args[1]["model"] == "gemini-2.5-pro"


def test_chatbot_node_logic(mock_personality):
    # We need to test the internal 'chatbot' function.
    # It's defined inside create_agent, so we can't import it directly.
    # However, we can construct the agent and then invoke the runnable,
    # OR we can extract the node function if we had access.
    # But for full coverage, we just need to run the graph or Mock the LLM correctly.

    with patch.object(Config, "LLM_PROVIDER", "google"):
        with patch("src.agent.ChatGoogleGenerativeAI") as MockLLMClass:
            mock_llm = MagicMock()
            MockLLMClass.return_value = mock_llm
            mock_llm.bind_tools.return_value = mock_llm  # mock the bound llm

            mock_response = AIMessage(content="Hello")
            mock_llm.invoke.return_value = mock_response

            app = create_agent(mock_personality)

            # Now we need to actually run the 'chatbot' node function.
            # Since 'app' is the compiled graph, we can invoke it.

            result = app.invoke(
                {"messages": [HumanMessage(content="Hi")]},
                config={"configurable": {"thread_id": "1"}},
            )

            assert result["messages"][-1].content == "Hello"

            # Verify that invoke was called with SystemMessage
            args, _ = mock_llm.invoke.call_args
            messages_passed = args[0]
            assert isinstance(messages_passed[0], SystemMessage)
            assert "2026" in messages_passed[0].content
