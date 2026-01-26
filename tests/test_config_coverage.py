import json
from unittest.mock import patch

import pytest

from src.config import Config, Personality

# --- Tests for src/config.py ---


def test_personality_model():
    p = Personality(
        name="Test",
        byline="Test Byline",
        identity=["Identity 1"],
        behavior=["Behavior 1"],
    )
    assert p.name == "Test"
    assert p.profile_image is None


def test_config_load_personalities_no_dir():
    with patch("pathlib.Path.exists", return_value=False):
        personalities = Config.load_personalities("dummy_path")
        assert personalities == {}


def test_config_load_personalities_valid(tmp_path):
    p_dir = tmp_path / "personalities"
    p_dir.mkdir()
    p_file = p_dir / "test.json"
    data = {
        "name": "Sacha",
        "byline": "AI",
        "identity": ["I am AI"],
        "behavior": ["Helpful"],
    }
    p_file.write_text(json.dumps(data), encoding="utf-8")

    personalities = Config.load_personalities(str(p_dir))
    assert "sacha" in personalities
    assert personalities["sacha"].name == "Sacha"


def test_config_load_personalities_invalid_json(tmp_path, capsys):
    p_dir = tmp_path / "personalities"
    p_dir.mkdir()
    p_file = p_dir / "bad.json"
    p_file.write_text("{invalid_json", encoding="utf-8")

    personalities = Config.load_personalities(str(p_dir))
    assert personalities == {}
    # Check stdout/stderr for error message if needed, but the function prints.
    captured = capsys.readouterr()
    assert "Error loading personality" in captured.out


def test_config_validate_success():
    with patch.object(Config, "GOOGLE_API_KEY", "dummy_key"):
        with patch.object(Config, "LLM_PROVIDER", "google"):
            Config.validate()  # Should not raise


def test_config_validate_fail_google():
    with patch.object(Config, "GOOGLE_API_KEY", None):
        with patch.object(Config, "LLM_PROVIDER", "google"):
            with pytest.raises(
                ValueError, match="GOOGLE_API_KEY environment variable is not set"
            ):
                Config.validate()
