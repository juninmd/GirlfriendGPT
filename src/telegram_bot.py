import logging
import asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters
from src.config import Config
from src.agent import GirlfriendAgent
from langchain_core.messages import HumanMessage, AIMessage

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Global agent instance (per chat ideally, but for now simple global or map)
# To handle multiple users, we should probably instantiate an agent per user_id or chat_id
# and store it in a dict.
agents = {}

def get_agent(chat_id: int):
    if chat_id not in agents:
        agents[chat_id] = {
            "agent": GirlfriendAgent(personality_name=Config.DEFAULT_PERSONALITY),
            "history": []
        }
    return agents[chat_id]

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_data = get_agent(update.effective_chat.id)
    agent = user_data["agent"]

    welcome_msg = f"Hi! I'm {agent.personality.name}. {agent.personality.byline}"
    await context.bot.send_message(chat_id=update.effective_chat.id, text=welcome_msg)

async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return

    chat_id = update.effective_chat.id
    user_data = get_agent(chat_id)
    agent = user_data["agent"]
    history = user_data["history"]

    user_text = update.message.text

    # Indicate typing
    await context.bot.send_chat_action(chat_id=chat_id, action="typing")

    # Run agent in executor to avoid blocking async loop
    loop = asyncio.get_running_loop()

    try:
        # We need to run the blocking agent code in a thread
        # Note: history passed to agent.chat is modified/returned
        new_history = await loop.run_in_executor(None, agent.chat, user_text, history)

        # Update history
        user_data["history"] = new_history

        # Get last message
        last_message = new_history[-1]
        response_text = last_message.content

        await context.bot.send_message(chat_id=chat_id, text=response_text)

    except Exception as e:
        logging.error(f"Error processing message: {e}")
        await context.bot.send_message(chat_id=chat_id, text="[I am having a headache... try again later?]")

def run_bot():
    if not Config.TELEGRAM_TOKEN:
        print("Error: TELEGRAM_TOKEN not found. Cannot start bot.")
        return

    application = ApplicationBuilder().token(Config.TELEGRAM_TOKEN).build()

    start_handler = CommandHandler('start', start)
    msg_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), message_handler)

    application.add_handler(start_handler)
    application.add_handler(msg_handler)

    print("Starting Telegram Bot...")
    application.run_polling()

if __name__ == "__main__":
    run_bot()
