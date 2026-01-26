from unittest.mock import patch, MagicMock
from src.tools import SelfieTool
from src.config import Config


class TestSelfieToolPerf:
    def test_client_instantiation_count(self):
        # Patch Config.GOOGLE_API_KEY to ensure tool attempts to create client
        with patch.object(Config, "GOOGLE_API_KEY", "dummy_key"):
            with patch("src.tools.genai.Client") as MockClient:
                # Setup mock to return a valid response so _run completes
                mock_response = MagicMock()
                mock_image = MagicMock()
                mock_image.image.image_bytes = b"fake_bytes"
                mock_response.generated_images = [mock_image]

                MockClient.return_value.models.generate_images.return_value = (
                    mock_response
                )

                tool = SelfieTool()

                # Run twice
                with patch("src.tools.tempfile.NamedTemporaryFile"):
                    tool._run("test 1")
                    tool._run("test 2")

                # Check instantiation count
                # Expected to be 1 after optimization
                print(f"\nClient instantiated {MockClient.call_count} times")
                assert MockClient.call_count == 1
