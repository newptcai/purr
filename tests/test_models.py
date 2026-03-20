import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock
import typer
import sys


def test_list_models(capsys):
    """Test that list_models outputs the correct format."""
    from kitten_cli.models import list_models
    
    # Capture stdout
    list_models()
    captured = capsys.readouterr()
    
    # Check that all expected models are listed
    expected_models = ["mini", "micro", "nano", "nano-int8"]
    for model in expected_models:
        assert model in captured.out
    
    # Check that status indicators are present
    assert "[installed]" in captured.out or "[not installed]" in captured.out


def test_is_model_downloaded_false(tmp_path):
    from kitten_cli import config
    import importlib
    
    with patch.object(config, "MODELS_DIR", tmp_path):
        # Force reimport to avoid test pollution
        if 'kitten_cli.models' in sys.modules:
            del sys.modules['kitten_cli.models']
        from kitten_cli.models import is_model_downloaded
        assert not is_model_downloaded("nano")


def test_is_model_downloaded_true(tmp_path):
    model_dir = tmp_path / "nano"
    model_dir.mkdir()
    (model_dir / "model.onnx").write_bytes(b"fake")

    # Import config first, then patch it
    from kitten_cli import config
    original_models_dir = config.MODELS_DIR
    
    try:
        # Patch the config module's MODELS_DIR
        config.MODELS_DIR = tmp_path
        
        # Force reimport to avoid test pollution
        if 'kitten_cli.models' in sys.modules:
            del sys.modules['kitten_cli.models']
        
        # Import models module after patching config
        from kitten_cli.models import is_model_downloaded
        assert is_model_downloaded("nano")
    finally:
        # Restore original value
        config.MODELS_DIR = original_models_dir


def test_remove_model_unknown(tmp_path):
    import typer
    from kitten_cli import config
    
    original_models_dir = config.MODELS_DIR
    try:
        config.MODELS_DIR = tmp_path
        
        # Force reimport to avoid test pollution
        if 'kitten_cli.models' in sys.modules:
            del sys.modules['kitten_cli.models']
        
        from kitten_cli.models import remove_model
        
        # typer.Exit is a subclass of SystemExit, but we need to catch it specifically
        with pytest.raises(typer.Exit) as exc_info:
            remove_model("nonexistent")
        assert exc_info.value.exit_code == 1
    finally:
        config.MODELS_DIR = original_models_dir


def test_remove_model_not_installed(tmp_path):
    import typer
    from kitten_cli import config
    
    original_models_dir = config.MODELS_DIR
    try:
        config.MODELS_DIR = tmp_path
        
        # Force reimport to avoid test pollution
        if 'kitten_cli.models' in sys.modules:
            del sys.modules['kitten_cli.models']
        
        from kitten_cli.models import remove_model
        
        with pytest.raises(typer.Exit) as exc_info:
            remove_model("nano")
        assert exc_info.value.exit_code == 1
    finally:
        config.MODELS_DIR = original_models_dir


def test_remove_model_success(tmp_path):
    model_dir = tmp_path / "nano"
    model_dir.mkdir()
    (model_dir / "model.onnx").write_bytes(b"fake")

    from kitten_cli import config
    original_models_dir = config.MODELS_DIR
    try:
        config.MODELS_DIR = tmp_path
        
        # Force reimport to avoid test pollution
        if 'kitten_cli.models' in sys.modules:
            del sys.modules['kitten_cli.models']
        
        from kitten_cli.models import remove_model
        remove_model("nano")
        assert not model_dir.exists()
    finally:
        config.MODELS_DIR = original_models_dir



