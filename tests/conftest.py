# Pytest configuration and fixtures for kitten-cli tests
# This ensures all tests use mock kittentts and avoid CUDA/torch downloads

import sys
import os
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest


# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


@pytest.fixture(autouse=True, scope="session")
def setup_mock_kittentts():
    """
    Global fixture that replaces kittentts with our mock implementation.
    This runs once for the entire test session and ensures no real kittentts
    imports can happen, preventing CUDA/torch downloads.
    """
    # Create a mock kittentts module
    mock_kittentts = MagicMock()
    
    # Import our mock implementation
    from tests.mock_kittentts import KittenTTS, __version__
    
    # Set up the mock module structure
    mock_kittentts.KittenTTS = KittenTTS
    mock_kittentts.__version__ = __version__
    
    # Add the mock to sys.modules before any real imports can happen
    sys.modules["kittentts"] = mock_kittentts
    
    # Set environment variables to prevent network access
    os.environ["HF_HUB_OFFLINE"] = "1"
    os.environ["KITTEN_CLI_TEST_MODE"] = "1"
    
    yield
    
    # Cleanup
    if "kittentts" in sys.modules:
        del sys.modules["kittentts"]
    if "HF_HUB_OFFLINE" in os.environ:
        del os.environ["HF_HUB_OFFLINE"]
    if "KITTEN_CLI_TEST_MODE" in os.environ:
        del os.environ["KITTEN_CLI_TEST_MODE"]


@pytest.fixture
def mock_models_dir(tmp_path):
    """Fixture that provides a temporary models directory for testing."""
    # Mock the config module's MODELS_DIR
    from kitten_cli import config
    original_models_dir = config.MODELS_DIR
    
    # Set up temporary models directory
    models_dir = tmp_path / "models"
    models_dir.mkdir()
    
    with patch.object(config, "MODELS_DIR", models_dir):
        yield models_dir
    
    # Restore original
    config.MODELS_DIR = original_models_dir


@pytest.fixture
def mock_audio_data():
    """Fixture that provides mock audio data for testing."""
    import numpy as np
    sample_rate = 24000
    duration = 1.0  # 1 second
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    # Generate a simple sine wave
    audio = np.sin(2 * np.pi * 440 * t).astype(np.float32) * 0.1
    return audio, sample_rate


@pytest.fixture
def installed_model(mock_models_dir):
    """Fixture that sets up a mock installed model."""
    model_name = "nano"
    model_dir = mock_models_dir / model_name
    model_dir.mkdir()
    (model_dir / "model.onnx").write_bytes(b"mock model data")
    (model_dir / "config.json").write_bytes(b'{"sample_rate": 24000}')
    return model_name, model_dir