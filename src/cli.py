import sys
import os

# Ensure src is in path
sys.path.append(os.getcwd())

from src.agent import GirlfriendAgent
from langchain_core.messages import HumanMessage, AIMessage

def main():
    print("Initializing GirlfriendGPT CLI...")

    # Check for keys but don't crash, let agent handle it
    agent = GirlfriendAgent(personality_name="luna")

    chat_history = []

    print(f"You are now chatting with {agent.personality.name}. Type 'quit' to exit.")

    while True:
        try:
            user_input = input("You: ")
            if user_input.lower() in ["quit", "exit"]:
                break

            print("Thinking...", end="\r")

            # The agent returns the full updated list of messages
            # We pass the accumulated history so far (excluding the system prompt which agent handles internally,
            # but wait, agent logic in _call_model prepends system prompt if missing.
            # To avoid duplicating system prompt in history, we should only pass user/ai messages.

            # Resetting history for the call to contain only conversation
            # The agent.chat method expects a list of messages.

            # Let's clean up how we handle history.
            # We will pass the conversation history.

            messages = agent.chat(user_input, history=chat_history)

            # Update chat history with the new messages
            # The graph returns all messages including the system prompt and tool calls
            # We should filter or just take the last response?
            # LangGraph returns the FINAL state.

            # Let's extract the last message
            response = messages[-1]

            # Print response
            print(f"{agent.personality.name}: {response.content}")

            # We need to keep the history state consistent for the next turn.
            # The 'messages' returned by the graph is the FULL conversation including what we sent + new stuff.
            # So we can just update chat_history to be this list, but we should be careful about the SystemMessage.

            # Remove SystemMessage from history if we want to keep it clean,
            # or just keep it. The agent code handles ensuring it's there.

            # To avoid SystemPrompt duplication if we pass it back in:
            # The agent code says: if not isinstance(messages[0], SystemMessage): prepend it.
            # If we pass back a list that HAS a SystemMessage, it updates it.
            # So it is safe to just set chat_history = messages.

            chat_history = messages

        except Exception as e:
            print(f"\nError: {e}")
            break

if __name__ == "__main__":
    main()
