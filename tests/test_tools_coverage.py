import pytest
import asyncio
from unittest.mock import patch, MagicMock, AsyncMock
from src.tools import SelfieTool, VoiceTool
from src.config import Config

# --- Tests for src/tools.py ---

class TestSelfieTool:
    def test_run_no_api_key(self):
        with patch.object(Config, "GOOGLE_API_KEY", None):
            tool = SelfieTool()
            result = tool._run("test")
            assert "missing GOOGLE_API_KEY" in result

    def test_run_success(self):
        with patch.object(Config, "GOOGLE_API_KEY", "dummy"):
            with patch("src.tools.genai.Client") as MockClient:
                mock_response = MagicMock()
                mock_image = MagicMock()
                mock_image.image.image_bytes = b"fake_image_bytes"
                mock_response.generated_images = [mock_image]

                MockClient.return_value.models.generate_images.return_value = mock_response

                tool = SelfieTool()
                with patch("src.tools.tempfile.NamedTemporaryFile") as MockTemp:
                    mock_temp_file = MagicMock()
                    mock_temp_file.name = "temp.png"
                    MockTemp.return_value.__enter__.return_value = mock_temp_file

                    result = tool._run("a selfie")
                    assert "IMAGE_GENERATED:temp.png" in result

    def test_run_failure_no_images(self):
        with patch.object(Config, "GOOGLE_API_KEY", "dummy"):
            with patch("src.tools.genai.Client") as MockClient:
                mock_response = MagicMock()
                mock_response.generated_images = []

                MockClient.return_value.models.generate_images.return_value = mock_response

                tool = SelfieTool()
                result = tool._run("a selfie")
                assert "Failed to generate image" in result

    def test_run_exception(self):
        with patch.object(Config, "GOOGLE_API_KEY", "dummy"):
            with patch("src.tools.genai.Client") as MockClient:
                MockClient.return_value.models.generate_images.side_effect = Exception("API Error")

                tool = SelfieTool()
                result = tool._run("a selfie")
                assert "Error generating selfie: API Error" in result

    @pytest.mark.asyncio
    async def test_arun(self):
         tool = SelfieTool()
         with patch.object(tool, "_run", return_value="success") as mock_run:
             result = await tool._arun("test")
             assert result == "success"
             mock_run.assert_called_once_with("test")


class TestVoiceTool:
    @pytest.mark.asyncio
    async def test_arun_no_voice(self):
        with patch.object(Config, "EDGE_TTS_VOICE", None):
            tool = VoiceTool()
            result = await tool._arun("test")
            assert "missing EDGE_TTS_VOICE" in result

    @pytest.mark.asyncio
    async def test_arun_success(self):
        with patch.object(Config, "EDGE_TTS_VOICE", "en-US"):
            tool = VoiceTool()
            with patch("src.tools.edge_tts.Communicate") as MockComm:
                mock_comm_instance = AsyncMock()
                MockComm.return_value = mock_comm_instance

                with patch("src.tools.tempfile.NamedTemporaryFile") as MockTemp:
                    mock_temp_file = MagicMock()
                    mock_temp_file.name = "temp.mp3"
                    MockTemp.return_value.__enter__.return_value = mock_temp_file

                    result = await tool._arun("hello")
                    assert "AUDIO_GENERATED:temp.mp3" in result
                    mock_comm_instance.save.assert_awaited_once_with("temp.mp3")

    @pytest.mark.asyncio
    async def test_arun_exception(self):
        with patch.object(Config, "EDGE_TTS_VOICE", "en-US"):
            with patch("src.tools.edge_tts.Communicate", side_effect=Exception("TTS Error")):
                tool = VoiceTool()
                result = await tool._arun("hello")
                assert "Error generating voice: TTS Error" in result

    def test_run_success(self):
        # This test is tricky because asyncio.run might clash with existing loop if not careful.
        # But pytest-asyncio handles loop management.
        # However, _run calls asyncio.run.

        tool = VoiceTool()
        with patch.object(tool, "_arun", new_callable=AsyncMock) as mock_arun:
            mock_arun.return_value = "success"
            result = tool._run("test")
            assert result == "success"

    def test_run_loop_running_error(self):
        tool = VoiceTool()
        # Mock asyncio.run to raise RuntimeError indicating loop is running
        with patch("asyncio.run", side_effect=RuntimeError("Loop running")):
             result = tool._run("test")
             assert "Async event loop already running" in result
