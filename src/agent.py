import operator
from typing import Annotated, List, TypedDict, Union

from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage, AIMessage, ToolMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode

from src.config import Config, Personality
from src.tools import get_tools

# Define the state
class AgentState(TypedDict):
    messages: Annotated[List[BaseMessage], operator.add]

class GirlfriendAgent:
    def __init__(self, personality_name: str = "luna"):
        self.personality = Config.load_personality(personality_name)
        self.tools = get_tools()

        # Initialize LLM (Gemini)
        # We use a model that supports tools
        if Config.GOOGLE_API_KEY:
            self.llm = ChatGoogleGenerativeAI(
                model="gemini-1.5-flash",
                temperature=0.7,
                google_api_key=Config.GOOGLE_API_KEY
            ).bind_tools(self.tools)
        else:
            # Fallback for testing without keys
            print("No Google API Key found. Agent will fail if invoked.")
            self.llm = None

        self.graph = self._build_graph()

    def _get_system_prompt(self) -> str:
        identity = "\n".join(self.personality.identity)
        behavior = "\n".join(self.personality.behavior)

        prompt = f"""You are {self.personality.name}, {self.personality.byline}.

Who you are:
{identity}

How you behave:
{behavior}

Stay in character at all times. You are NOT an AI assistant. You are {self.personality.name}.
"""
        return prompt

    def _call_model(self, state: AgentState):
        messages = state["messages"]

        # Ensure system prompt is first
        if not isinstance(messages[0], SystemMessage):
             messages = [SystemMessage(content=self._get_system_prompt())] + messages
        else:
             # Update system prompt just in case personality changed (not handled yet but good practice)
             messages[0] = SystemMessage(content=self._get_system_prompt())

        if not self.llm:
            return {"messages": [AIMessage(content="[System Error: No Brain Connected]")]}

        response = self.llm.invoke(messages)
        return {"messages": [response]}

    def _should_continue(self, state: AgentState):
        messages = state["messages"]
        last_message = messages[-1]

        if last_message.tool_calls:
            return "tools"
        return END

    def _build_graph(self):
        workflow = StateGraph(AgentState)

        workflow.add_node("agent", self._call_model)
        workflow.add_node("tools", ToolNode(self.tools))

        workflow.set_entry_point("agent")

        workflow.add_conditional_edges(
            "agent",
            self._should_continue,
        )

        workflow.add_edge("tools", "agent")

        return workflow.compile()

    def chat(self, user_input: str, history: List[BaseMessage] = None):
        if history is None:
            history = []

        # We only pass the new message to the graph, assuming history is managed via the state check?
        # LangGraph state is usually ephemeral per run, so we need to pass the full history or rely on the caller to maintain it.
        # For simplicity here, we accept history and append the user input.

        inputs = {"messages": history + [HumanMessage(content=user_input)]}

        # Run the graph
        final_state = self.graph.invoke(inputs)

        return final_state["messages"]
