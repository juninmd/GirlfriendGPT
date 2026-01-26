from typing import Annotated, Any, Dict, TypedDict, Union

from langchain_core.messages import BaseMessage, SystemMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_ollama import ChatOllama
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition

import logging
from src.config import Config, Personality
from src.tools import SelfieTool, VoiceTool

# Configure logging
logger = logging.getLogger(__name__)

# Define the tools
tools = [SelfieTool(), VoiceTool()]


# Define the state
class AgentState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]


def create_agent(personality: Personality) -> Any:
    # Initialize LLM based on provider
    llm: Union[ChatOllama, ChatGoogleGenerativeAI]
    if Config.LLM_PROVIDER == "ollama":
        logger.info(f"Initializing agent with Ollama model: {Config.OLLAMA_MODEL}")
        llm = ChatOllama(
            model=Config.OLLAMA_MODEL,
            base_url=Config.OLLAMA_BASE_URL,
            temperature=0.8,
        )
    else:
        # Default to Google Gemini
        logger.info(f"Initializing agent with Google model: {Config.GOOGLE_MODEL}")
        llm = ChatGoogleGenerativeAI(
            model=Config.GOOGLE_MODEL,
            api_key=Config.GOOGLE_API_KEY,
            temperature=0.8,
            max_tokens=None,
            timeout=None,
            max_retries=2,
        )

    # Bind tools
    llm_with_tools = llm.bind_tools(tools)

    # System prompt
    system_prompt = f"""The current year is 2026.
You are {personality.name}, {personality.byline}.

Who you are:
{chr(10).join(personality.identity)}

How you behave:
{chr(10).join(personality.behavior)}

You have access to tools to take selfies and send voice messages.
If the user asks for a selfie or photo, use the SelfieTool.
If the user asks for a voice message or you want to speak, use the VoiceTool.
"""

    def chatbot(state: AgentState) -> Dict[str, Any]:
        messages = state["messages"]
        # Ensure system prompt is the first message if not present or needs update
        # For simplicity in this graph, we assume the system message is injected at
        # start of conversation or we prepend it here if we want to be stateless
        # regarding system prompt. But langgraph state accumulates.

        conversation_messages = [SystemMessage(content=system_prompt)] + messages
        response = llm_with_tools.invoke(conversation_messages)
        return {"messages": [response]}

    # Define the graph
    workflow = StateGraph(AgentState)

    workflow.add_node("chatbot", chatbot)
    workflow.add_node("tools", ToolNode(tools))

    workflow.set_entry_point("chatbot")

    workflow.add_conditional_edges(
        "chatbot",
        tools_condition,
    )
    workflow.add_edge("tools", "chatbot")

    # Compile the graph
    # We use MemorySaver for simple in-memory checkpointing during a session
    checkpointer = MemorySaver()
    app = workflow.compile(checkpointer=checkpointer)

    return app
