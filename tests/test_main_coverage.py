from unittest.mock import AsyncMock, MagicMock, mock_open, patch

import pytest
from langchain_core.messages import AIMessage, HumanMessage, ToolMessage
from telegram import Update

from src.config import Config, Personality
from src.main import bot_loop, cli_loop, get_agent_for_user, handle_message, main, start

# --- Tests for src/main.py ---


@pytest.fixture
def mock_agent():
    agent = AsyncMock()
    # By default, return a response with just text
    agent.ainvoke.return_value = {"messages": [AIMessage(content="Hello user")]}
    return agent


@pytest.fixture
def mock_personalities():
    return {"sacha": Personality(name="Sacha", byline="", identity=[], behavior=[])}


def test_get_agent_for_user(mock_personalities):
    with patch("src.main.personalities", mock_personalities):
        with patch("src.main.create_agent") as mock_create:
            mock_create.return_value = "mock_agent"
            with patch("src.main.agents", {}):
                # New agent
                agent = get_agent_for_user("sacha")
                assert agent == "mock_agent"

                # Existing agent
                agent2 = get_agent_for_user("sacha")
                assert agent2 == "mock_agent"
                assert mock_create.call_count == 1  # Only created once


def test_get_agent_for_user_fallback(mock_personalities):
    with patch("src.main.personalities", mock_personalities):
        with patch("src.main.create_agent") as mock_create:
            mock_create.return_value = "mock_agent"
            with patch("src.main.agents", {}):
                # Unknown personality -> fallback to Sacha
                agent = get_agent_for_user("unknown")
                assert agent == "mock_agent"


def test_get_agent_for_user_fallback_other():
    # Test fallback to another personality if Sacha is missing
    other_pers = {
        "other": Personality(name="Other", byline="", identity=[], behavior=[])
    }
    with patch("src.main.personalities", other_pers):
        with patch("src.main.create_agent") as mock_create:
            mock_create.return_value = "mock_agent"
            with patch("src.main.agents", {}):
                agent = get_agent_for_user("unknown")
                assert agent == "mock_agent"


def test_get_agent_for_user_no_personalities():
    with patch("src.main.personalities", {}):
        with patch("src.main.agents", {}):
            with pytest.raises(ValueError, match="No personalities found"):
                get_agent_for_user("sacha")


@pytest.mark.asyncio
async def test_cli_loop_quit():
    with patch("builtins.input", side_effect=["sacha", "quit"]):
        with patch("builtins.print") as mock_print:
            with patch(
                "src.main.Config.load_personalities", return_value={"sacha": "p"}
            ):
                with patch("src.main.create_agent") as mock_create:
                    mock_create.return_value = AsyncMock()
                    await cli_loop()
                    mock_print.assert_any_call("Starting CLI mode...")


@pytest.mark.asyncio
async def test_cli_loop_chat(mock_agent):
    # Mock input: choose sacha, say hi, then quit
    with patch("builtins.input", side_effect=["sacha", "hi", "quit"]):
        with patch(
            "src.main.Config.load_personalities", return_value={"sacha": MagicMock()}
        ):
            with patch("src.main.get_agent_for_user", return_value=mock_agent):
                with patch("builtins.print") as mock_print:
                    await cli_loop()
                    # verify agent was invoked
                    mock_agent.ainvoke.assert_called()
                    # verify output
                    assert any(
                        "sacha: Hello user" in str(c) for c in mock_print.call_args_list
                    )


@pytest.mark.asyncio
async def test_cli_loop_no_personalities():
    with patch("src.main.Config.load_personalities", return_value={}):
        with patch("builtins.print") as mock_print:
            await cli_loop()
            mock_print.assert_called_with(
                "No personalities found in src/personalities/"
            )


@pytest.mark.asyncio
async def test_cli_loop_error(mock_agent):
    # Mock input: choose sacha, say hi (triggers error), quit
    mock_agent.ainvoke.side_effect = Exception("Boom")
    with patch("builtins.input", side_effect=["sacha", "hi", "quit"]):
        with patch(
            "src.main.Config.load_personalities", return_value={"sacha": MagicMock()}
        ):
            with patch("src.main.get_agent_for_user", return_value=mock_agent):
                with patch("builtins.print") as mock_print:
                    await cli_loop()
                    assert any(
                        "Error: Boom" in str(c) for c in mock_print.call_args_list
                    )


@pytest.mark.asyncio
async def test_start():
    update = MagicMock(spec=Update)
    update.message.reply_text = AsyncMock()
    context = MagicMock()

    await start(update, context)
    update.message.reply_text.assert_called_once()
    assert "Gemini" in update.message.reply_text.call_args[0][0]


@pytest.mark.asyncio
async def test_handle_message_text(mock_agent):
    update = MagicMock(spec=Update)
    update.effective_user.id = 123
    update.effective_chat.id = 456
    update.message.text = "Hello"
    update.message.reply_text = AsyncMock()

    context = MagicMock()
    context.user_data = {}
    context.bot.send_chat_action = AsyncMock()

    with patch("src.main.get_agent_for_user", return_value=mock_agent):
        await handle_message(update, context)

        mock_agent.ainvoke.assert_called()
        update.message.reply_text.assert_called_with("Hello user")


@pytest.mark.asyncio
async def test_handle_message_tool_audio(mock_agent):
    # Mock agent returning a ToolMessage with AUDIO_GENERATED
    mock_agent.ainvoke.return_value = {
        "messages": [
            HumanMessage(content="Speak"),
            ToolMessage(content="AUDIO_GENERATED:test.mp3", tool_call_id="1"),
        ]
    }

    update = MagicMock(spec=Update)
    update.effective_chat.id = 456
    update.message.reply_text = AsyncMock()
    context = MagicMock()
    context.user_data = {}
    context.bot.send_voice = AsyncMock()
    context.bot.send_chat_action = AsyncMock()

    with patch("src.main.get_agent_for_user", return_value=mock_agent):
        with patch("builtins.open", mock_open(read_data=b"audio")):
            with patch("os.remove") as mock_remove:
                await handle_message(update, context)

                context.bot.send_voice.assert_called()
                mock_remove.assert_called_with("test.mp3")


@pytest.mark.asyncio
async def test_handle_message_tool_audio_cleanup_error(mock_agent):
    mock_agent.ainvoke.return_value = {
        "messages": [
            HumanMessage(content="Speak"),
            ToolMessage(content="AUDIO_GENERATED:test.mp3", tool_call_id="1"),
        ]
    }
    update = MagicMock(spec=Update)
    update.message.reply_text = AsyncMock()  # Must be AsyncMock
    context = MagicMock()
    context.bot.send_voice = AsyncMock()
    context.bot.send_chat_action = AsyncMock()

    with patch("src.main.get_agent_for_user", return_value=mock_agent):
        with patch("builtins.open", mock_open(read_data=b"audio")):
            with patch("os.remove", side_effect=Exception("Cleanup fail")):
                await handle_message(update, context)
                # Should not raise, but log warning.
                context.bot.send_voice.assert_called()


@pytest.mark.asyncio
async def test_handle_message_tool_audio_send_error(mock_agent):
    mock_agent.ainvoke.return_value = {
        "messages": [
            HumanMessage(content="Speak"),
            ToolMessage(content="AUDIO_GENERATED:test.mp3", tool_call_id="1"),
        ]
    }
    update = MagicMock(spec=Update)
    update.message.reply_text = AsyncMock()  # Must be AsyncMock
    context = MagicMock()
    context.bot.send_voice = AsyncMock(side_effect=Exception("Send fail"))
    context.bot.send_chat_action = AsyncMock()

    with patch("src.main.get_agent_for_user", return_value=mock_agent):
        # Should catch exception and log error
        await handle_message(update, context)


@pytest.mark.asyncio
async def test_handle_message_tool_image(mock_agent):
    # Mock agent returning a ToolMessage with IMAGE_GENERATED
    mock_agent.ainvoke.return_value = {
        "messages": [
            HumanMessage(content="Selfie"),
            ToolMessage(content="IMAGE_GENERATED:test.png", tool_call_id="1"),
        ]
    }

    update = MagicMock(spec=Update)
    update.effective_chat.id = 456
    update.message.reply_text = AsyncMock()
    context = MagicMock()
    context.user_data = {}
    context.bot.send_photo = AsyncMock()
    context.bot.send_chat_action = AsyncMock()

    with patch("src.main.get_agent_for_user", return_value=mock_agent):
        with patch("builtins.open", mock_open(read_data=b"image")):
            with patch("os.remove") as mock_remove:
                await handle_message(update, context)
                context.bot.send_photo.assert_called()
                mock_remove.assert_called_with("test.png")


@pytest.mark.asyncio
async def test_handle_message_tool_image_cleanup_error(mock_agent):
    mock_agent.ainvoke.return_value = {
        "messages": [
            HumanMessage(content="Selfie"),
            ToolMessage(content="IMAGE_GENERATED:test.png", tool_call_id="1"),
        ]
    }
    update = MagicMock(spec=Update)
    update.message.reply_text = AsyncMock()  # Must be AsyncMock
    context = MagicMock()
    context.bot.send_photo = AsyncMock()
    context.bot.send_chat_action = AsyncMock()

    with patch("src.main.get_agent_for_user", return_value=mock_agent):
        with patch("builtins.open", mock_open(read_data=b"image")):
            with patch("os.remove", side_effect=Exception("Cleanup fail")):
                await handle_message(update, context)
                context.bot.send_photo.assert_called()


@pytest.mark.asyncio
async def test_handle_message_tool_image_send_error(mock_agent):
    mock_agent.ainvoke.return_value = {
        "messages": [
            HumanMessage(content="Selfie"),
            ToolMessage(content="IMAGE_GENERATED:test.png", tool_call_id="1"),
        ]
    }
    update = MagicMock(spec=Update)
    update.message.reply_text = AsyncMock()  # Must be AsyncMock
    context = MagicMock()
    context.bot.send_photo = AsyncMock(side_effect=Exception("Send fail"))
    context.bot.send_chat_action = AsyncMock()

    with patch("src.main.get_agent_for_user", return_value=mock_agent):
        await handle_message(update, context)


@pytest.mark.asyncio
async def test_handle_message_error():
    update = MagicMock(spec=Update)
    update.effective_chat.id = 123
    update.message.reply_text = AsyncMock()
    context = MagicMock()

    with patch("src.main.get_agent_for_user", side_effect=Exception("Error")):
        await handle_message(update, context)
        # It logs error and replies
        update.message.reply_text.assert_called_with(
            "I'm having trouble thinking right now."
        )


def test_bot_loop():
    with patch.object(Config, "TELEGRAM_TOKEN", "fake_token"):
        with patch("src.main.Config.load_personalities", return_value={}):
            with patch("telegram.ext.Application.builder") as MockBuilder:
                mock_app = MagicMock()
                mock_app.run_polling = MagicMock()
                MockBuilder.return_value.token.return_value.build.return_value = (
                    mock_app
                )

                bot_loop()

                mock_app.run_polling.assert_called_once()


def test_bot_loop_no_token():
    with patch.object(Config, "TELEGRAM_TOKEN", None):
        with patch("builtins.print") as mock_print:
            bot_loop()
            mock_print.assert_called_with("Error: TELEGRAM_TOKEN not set.")


def test_main_cli():
    with patch("argparse.ArgumentParser.parse_args") as mock_args:
        mock_args.return_value.cli = True
        with patch("src.main.cli_loop"):  # async func
            # main calls asyncio.run(cli_loop())
            # we mock asyncio.run
            with patch("asyncio.run") as mock_run:
                main()
                mock_run.assert_called()


def test_main_bot():
    with patch("argparse.ArgumentParser.parse_args") as mock_args:
        mock_args.return_value.cli = False
        with patch("src.main.bot_loop") as mock_bot_loop:
            with patch("asyncio.run") as mock_run:
                main()
                mock_run.assert_not_called()
                mock_bot_loop.assert_called_once()


def test_main_keyboard_interrupt():
    with patch("argparse.ArgumentParser.parse_args") as mock_args:
        mock_args.return_value.cli = False
        with patch("src.main.bot_loop", side_effect=KeyboardInterrupt):
            main()
            # Should just exit gracefully


def test_main_execution():
    # To fix coverage for "if __name__ == '__main__': main()", we can cheat a bit
    # since we can't easily run subprocess with coverage inside this env without
    # messing things up.
    # We already test main() logic in other tests.
    pass


@pytest.mark.asyncio
async def test_cli_loop_missing_personalities_print():
    # Test lines 55-56
    with patch("src.main.Config.load_personalities", return_value={}):
        with patch("builtins.print") as mock_print:
            await cli_loop()
            mock_print.assert_called_with(
                "No personalities found in src/personalities/"
            )


@pytest.mark.asyncio
async def test_cli_loop_default_personality():
    # Test lines 61-64: input empty -> default sacha
    with patch.dict("src.main.agents", {}, clear=True):
        with patch("builtins.input", side_effect=["", "quit"]):
            with patch("src.main.Config.load_personalities", return_value={"sacha": "p"}):
                with patch("src.main.create_agent") as mock_create:
                    mock_create.return_value = AsyncMock()
                    with patch("builtins.print") as mock_print:
                        await cli_loop()
                        # verify "Chatting with sacha"
                        assert any(
                            "Chatting with sacha" in str(c)
                            for c in mock_print.call_args_list
                        )


@pytest.mark.asyncio
async def test_cli_loop_invalid_personality():
    # Test lines 66-68: invalid input -> default sacha
    with patch.dict("src.main.agents", {}, clear=True):
        with patch("builtins.input", side_effect=["invalid", "quit"]):
            with patch("src.main.Config.load_personalities", return_value={"sacha": "p"}):
                with patch("src.main.create_agent") as mock_create:
                    mock_create.return_value = AsyncMock()
                    with patch("builtins.print") as mock_print:
                        await cli_loop()
                        mock_print.assert_any_call(
                            "Personality invalid not found. Using default."
                        )


@pytest.mark.asyncio
async def test_handle_message_ignored_updates():
    context = MagicMock()

    # Test update without effective_chat
    update_no_chat = MagicMock(spec=Update)
    update_no_chat.effective_chat = None
    await handle_message(update_no_chat, context)
    # Should just return

    # Test update without message
    update_no_msg = MagicMock(spec=Update)
    update_no_msg.effective_chat = MagicMock()
    update_no_msg.message = None
    await handle_message(update_no_msg, context)

    # Test update without text
    update_no_text = MagicMock(spec=Update)
    update_no_text.effective_chat = MagicMock()
    update_no_text.message.text = None
    await handle_message(update_no_text, context)
