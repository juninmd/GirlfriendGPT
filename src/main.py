import argparse
import asyncio
import logging
import os
from typing import Dict, Any

from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from langchain_core.messages import HumanMessage, ToolMessage

from src.config import Config, Personality
from src.agent import create_agent

# Configure logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# Global agents cache: personality_name -> compiled_graph
agents: Dict[str, Any] = {}
# Global personalities
personalities: Dict[str, Personality] = {}

def get_agent_for_user(personality_name: str):
    if personality_name not in agents:
        p = personalities.get(personality_name.lower())
        if not p:
            # Fallback to first available or Sacha
            if "sacha" in personalities:
                p = personalities["sacha"]
            elif personalities:
                p = next(iter(personalities.values()))
            else:
                raise ValueError("No personalities found!")

        agents[personality_name] = create_agent(p)
    return agents[personality_name]

async def cli_loop():
    print("Starting CLI mode...")
    # Load personalities
    global personalities
    personalities = Config.load_personalities()
    if not personalities:
        print("No personalities found in src/personalities/")
        return

    # Select personality
    print("Available personalities:", ", ".join(personalities.keys()))
    p_name = input("Choose personality (default: sacha): ").strip() or "sacha"

    if p_name.lower() not in personalities:
        print(f"Personality {p_name} not found. Using default.")
        p_name = "sacha"

    agent = get_agent_for_user(p_name)
    thread_id = "cli_user"
    config = {"configurable": {"thread_id": thread_id}}

    print(f"Chatting with {p_name}. Type 'quit' to exit.")
    while True:
        user_input = input("You: ")
        if user_input.lower() in ["quit", "exit"]:
            break

        # Invoke agent
        # We need to stream or invoke
        try:
            input_message = HumanMessage(content=user_input)
            response = await agent.ainvoke({"messages": [input_message]}, config=config)

            # Extract last AI message
            last_msg = response["messages"][-1]
            print(f"{p_name}: {last_msg.content}")
        except Exception as e:
            print(f"Error: {e}")

# Telegram Bot Handlers

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.message:
        await update.message.reply_text("Hello! I'm your AI companion, powered by the latest Gemini technology (2026 Edition). How are you doing today?")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.effective_chat or not update.message or not update.message.text:
        return

    chat_id = update.effective_chat.id
    text = update.message.text

    # Determine personality. For now, hardcoded or stored in user_data
    # We could allow user to switch personalities.
    p_name = "sacha"
    if context.user_data:
        p_name = context.user_data.get("personality", "sacha")

    # Invoke agent
    try:
        agent = get_agent_for_user(p_name)
        thread_id = str(chat_id)
        config = {"configurable": {"thread_id": thread_id}}

        input_message = HumanMessage(content=text)
        # Show typing status
        await context.bot.send_chat_action(chat_id=chat_id, action="typing")

        response = await agent.ainvoke({"messages": [input_message]}, config=config)

        last_msg = response["messages"][-1]
        response_text = last_msg.content

        if update.message:
            await update.message.reply_text(response_text)

        # Handle media from tools
        messages = response["messages"]
        last_human_idx = -1
        # Find the last HumanMessage to scope our search
        for i, msg in enumerate(reversed(messages)):
            if isinstance(msg, HumanMessage):
                last_human_idx = len(messages) - 1 - i
                break

        if last_human_idx != -1:
            for msg in messages[last_human_idx+1:]:
                if isinstance(msg, ToolMessage):
                    content = str(msg.content)
                    if "AUDIO_GENERATED:" in content:
                        try:
                            path = content.split("AUDIO_GENERATED:")[1].strip()
                            await context.bot.send_chat_action(chat_id=chat_id, action="upload_voice")
                            with open(path, "rb") as audio:
                                await context.bot.send_voice(chat_id=chat_id, voice=audio)

                            # Cleanup
                            try:
                                os.remove(path)
                            except Exception as e:
                                logger.warning(f"Failed to remove temp file {path}: {e}")

                        except Exception as e:
                            logger.error(f"Failed to send voice: {e}")

                    if "IMAGE_GENERATED:" in content:
                        try:
                            path = content.split("IMAGE_GENERATED:")[1].strip()
                            await context.bot.send_chat_action(chat_id=chat_id, action="upload_photo")
                            with open(path, "rb") as photo:
                                await context.bot.send_photo(chat_id=chat_id, photo=photo)

                            # Cleanup
                            try:
                                os.remove(path)
                            except Exception as e:
                                logger.warning(f"Failed to remove temp file {path}: {e}")

                        except Exception as e:
                            logger.error(f"Failed to send photo: {e}")

    except Exception as e:
        logger.error(f"Error processing message: {e}")
        if update.message:
            await update.message.reply_text("I'm having trouble thinking right now.")

async def bot_loop():
    if not Config.TELEGRAM_TOKEN:
        print("Error: TELEGRAM_TOKEN not set.")
        return

    # Load personalities
    global personalities
    personalities = Config.load_personalities()

    application = Application.builder().token(Config.TELEGRAM_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("Starting Telegram Bot polling...")
    await application.run_polling(allowed_updates=Update.ALL_TYPES)

def main():
    parser = argparse.ArgumentParser(description="GirlfriendGPT 2026")
    parser.add_argument("--cli", action="store_true", help="Run in CLI mode")
    args = parser.parse_args()

    print("---------------------------------------")
    print("GirlfriendGPT - 2026 Edition")
    print("Powered by Google Gemini 2.5 Pro")
    print("---------------------------------------")

    # Run async loop
    try:
        if args.cli:
            asyncio.run(cli_loop())
        else:
            asyncio.run(bot_loop())
    except KeyboardInterrupt:
        pass

if __name__ == "__main__":
    main()  # pragma: no cover
