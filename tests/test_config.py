# Config module tests for kitten-cli
import pytest
from pathlib import Path


def test_model_registry():
    """Test that MODEL_REGISTRY contains expected models."""
    from kitten_cli.config import MODEL_REGISTRY
    
    expected_models = ["mini", "micro", "nano", "nano-int8"]
    expected_repos = [
        "KittenML/kitten-tts-mini-0.8",
        "KittenML/kitten-tts-micro-0.8", 
        "KittenML/kitten-tts-nano-0.8",
        "KittenML/kitten-tts-nano-0.8-int8",
    ]
    
    # Check all expected models are present
    assert set(MODEL_REGISTRY.keys()) == set(expected_models)
    
    # Check the repo IDs are correct
    for model, expected_repo in zip(expected_models, expected_repos):
        assert MODEL_REGISTRY[model] == expected_repo


def test_default_values():
    """Test that default values are set correctly."""
    from kitten_cli.config import DEFAULT_MODEL, DEFAULT_VOICE, DEFAULT_SPEED, SAMPLE_RATE
    
    # These should be set to reasonable defaults
    assert DEFAULT_MODEL in ["mini", "micro", "nano", "nano-int8"]
    assert isinstance(DEFAULT_VOICE, str)
    assert len(DEFAULT_VOICE) > 0
    assert isinstance(DEFAULT_SPEED, float)
    assert DEFAULT_SPEED > 0
    assert SAMPLE_RATE == 24000


def test_models_dir_path():
    """Test that MODELS_DIR is a valid Path object."""
    from kitten_cli.config import MODELS_DIR
    
    assert isinstance(MODELS_DIR, Path)
    assert str(MODELS_DIR).endswith("kitten-cli/models")


def test_best_installed_model():
    """Test the _best_installed_model function."""
    from kitten_cli.config import _best_installed_model, MODEL_REGISTRY
    
    # The function should return one of the known model aliases
    result = _best_installed_model()
    assert result in MODEL_REGISTRY


def test_cache_base_xdg():
    """Test that cache base respects XDG_CACHE_HOME if set."""
    import os
    from pathlib import Path
    
    # Save original value
    original_xdg = os.environ.get("XDG_CACHE_HOME", "")
    
    try:
        # Test with XDG_CACHE_HOME set
        test_cache_dir = "/tmp/test_cache"
        os.environ["XDG_CACHE_HOME"] = test_cache_dir
        
        # Reimport to pick up the new environment variable
        import importlib
        import kitten_cli.config
        importlib.reload(kitten_cli.config)
        
        from kitten_cli.config import CACHE_BASE
        expected = Path(test_cache_dir)
        assert CACHE_BASE == expected
        
    finally:
        # Restore original value
        if original_xdg:
            os.environ["XDG_CACHE_HOME"] = original_xdg
        elif "XDG_CACHE_HOME" in os.environ:
            del os.environ["XDG_CACHE_HOME"]
        
        # Reload to restore original behavior
        importlib.reload(kitten_cli.config)


def test_model_priority_order():
    """Test that _MODEL_PRIORITY contains all models in correct order."""
    from kitten_cli.config import _MODEL_PRIORITY, MODEL_REGISTRY
    
    # Should contain all models
    assert set(_MODEL_PRIORITY) == set(MODEL_REGISTRY.keys())
    
    # Should be in priority order (best first)
    # This is a bit subjective, but we can check the general pattern
    assert "mini" in _MODEL_PRIORITY
    assert "nano-int8" in _MODEL_PRIORITY
    
    # mini should come before nano-int8 (better quality first)
    assert _MODEL_PRIORITY.index("mini") < _MODEL_PRIORITY.index("nano-int8")