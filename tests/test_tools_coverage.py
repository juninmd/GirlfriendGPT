from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.config import Config
from src.tools import SelfieTool, VoiceTool

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

                MockClient.return_value.models.generate_images.return_value = (
                    mock_response
                )

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

                MockClient.return_value.models.generate_images.return_value = (
                    mock_response
                )

                tool = SelfieTool()
                result = tool._run("a selfie")
                assert "Failed to generate image" in result

    def test_run_failure_no_image_bytes(self):
        with patch.object(Config, "GOOGLE_API_KEY", "dummy"):
            with patch("src.tools.genai.Client") as MockClient:
                mock_response = MagicMock()
                mock_image = MagicMock()
                mock_image.image.image_bytes = None
                mock_response.generated_images = [mock_image]

                MockClient.return_value.models.generate_images.return_value = (
                    mock_response
                )

                tool = SelfieTool()
                result = tool._run("a selfie")
                assert "Failed to generate image" in result

    def test_run_exception(self):
        with patch.object(Config, "GOOGLE_API_KEY", "dummy"):
            with patch("src.tools.genai.Client") as MockClient:
                MockClient.return_value.models.generate_images.side_effect = Exception(
                    "API Error"
                )

                tool = SelfieTool()
                result = tool._run("a selfie")
                assert "Error generating selfie: API Error" in result

    @pytest.mark.asyncio
    async def test_arun(self):
        with patch.object(Config, "GOOGLE_API_KEY", "dummy"):
            with patch("src.tools.genai.Client") as MockClient:
                # Mock aio.models.generate_images
                mock_response = MagicMock()
                mock_image = MagicMock()
                mock_image.image.image_bytes = b"fake_bytes"
                mock_response.generated_images = [mock_image]

                # Setup async mock for generate_images
                mock_generate = AsyncMock(return_value=mock_response)

                # Mock client structure: client.aio.models.generate_images
                mock_client_instance = MockClient.return_value
                mock_client_instance.aio.models.generate_images = mock_generate

                tool = SelfieTool()

                with patch("src.tools.tempfile.NamedTemporaryFile") as MockTemp:
                    mock_temp_file = MagicMock()
                    mock_temp_file.name = "temp.png"
                    MockTemp.return_value.__enter__.return_value = mock_temp_file

                    result = await tool._arun("test prompt")

                    assert "IMAGE_GENERATED:temp.png" in result
                    mock_generate.assert_awaited_once()
                    # Verify model and prompt
                    args, kwargs = mock_generate.await_args
                    assert kwargs["model"] == "imagen-3.0-generate-001"
                    assert kwargs["prompt"] == "test prompt"

    @pytest.mark.asyncio
    async def test_arun_no_api_key(self):
        with patch.object(Config, "GOOGLE_API_KEY", None):
            tool = SelfieTool()
            result = await tool._arun("test")
            assert "missing GOOGLE_API_KEY" in result

    @pytest.mark.asyncio
    async def test_arun_exception(self):
        with patch.object(Config, "GOOGLE_API_KEY", "dummy"):
            with patch("src.tools.genai.Client") as MockClient:
                mock_generate = AsyncMock(side_effect=Exception("Async Error"))
                MockClient.return_value.aio.models.generate_images = mock_generate

                tool = SelfieTool()
                result = await tool._arun("test")
                assert "Error generating selfie: Async Error" in result

    @pytest.mark.asyncio
    async def test_arun_failure_no_images(self):
        with patch.object(Config, "GOOGLE_API_KEY", "dummy"):
            with patch("src.tools.genai.Client") as MockClient:
                mock_response = MagicMock()
                mock_response.generated_images = []
                mock_generate = AsyncMock(return_value=mock_response)
                MockClient.return_value.aio.models.generate_images = mock_generate

                tool = SelfieTool()
                result = await tool._arun("test")
                assert "Failed to generate image" in result

    @pytest.mark.asyncio
    async def test_arun_failure_no_image_bytes(self):
        with patch.object(Config, "GOOGLE_API_KEY", "dummy"):
            with patch("src.tools.genai.Client") as MockClient:
                mock_response = MagicMock()
                mock_image = MagicMock()
                mock_image.image.image_bytes = None
                mock_response.generated_images = [mock_image]

                mock_generate = AsyncMock(return_value=mock_response)
                MockClient.return_value.aio.models.generate_images = mock_generate

                tool = SelfieTool()
                result = await tool._arun("test")
                assert "Failed to generate image" in result


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
            with patch(
                "src.tools.edge_tts.Communicate", side_effect=Exception("TTS Error")
            ):
                tool = VoiceTool()
                result = await tool._arun("hello")
                assert "Error generating voice: TTS Error" in result

    def test_run_success(self):
        # This test is tricky because asyncio.run might clash with existing loop if
        # not careful.
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
