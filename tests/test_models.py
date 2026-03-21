# Models module tests for kitten-cli
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock
import typer


def test_list_models(capsys, mock_models_dir):
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


def test_is_model_downloaded_false(mock_models_dir):
    """Test is_model_downloaded returns False when model dir doesn't exist."""
    from kitten_cli.models import is_model_downloaded
    assert not is_model_downloaded("nano")


def test_is_model_downloaded_true(mock_models_dir):
    """Test is_model_downloaded returns True when model dir exists."""
    model_dir = mock_models_dir / "nano"
    model_dir.mkdir()
    (model_dir / "model.onnx").write_bytes(b"fake")

    from kitten_cli.models import is_model_downloaded
    assert is_model_downloaded("nano")


def test_remove_model_unknown(mock_models_dir):
    """Test remove_model with unknown model alias."""
    from kitten_cli.models import remove_model
    
    # typer.Exit is a subclass of SystemExit
    with pytest.raises(typer.Exit) as exc_info:
        remove_model("nonexistent")
    assert exc_info.value.exit_code == 1


def test_remove_model_not_installed(mock_models_dir):
    """Test remove_model with model that isn't installed."""
    from kitten_cli.models import remove_model
    
    with pytest.raises(typer.Exit) as exc_info:
        remove_model("nano")
    assert exc_info.value.exit_code == 1


def test_remove_model_success(mock_models_dir):
    """Test remove_model successfully removes model directory."""
    model_dir = mock_models_dir / "nano"
    model_dir.mkdir()
    (model_dir / "model.onnx").write_bytes(b"fake")

    from kitten_cli.models import remove_model
    remove_model("nano")
    assert not model_dir.exists()


def test_install_model_success(mock_models_dir):
    """Test install_model successfully installs a model."""
    from kitten_cli.models import install_model
    
    # Install nano
    install_model("nano")
    
    # Verify installation directory
    model_dir = mock_models_dir / "nano"
    assert model_dir.exists()
