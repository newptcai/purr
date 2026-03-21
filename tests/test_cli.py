# CLI command tests for kitten-cli
import pytest
from pathlib import Path
from typer.testing import CliRunner


def test_model_list_command(mock_models_dir):
    """Test the 'purr model list' command."""
    from kitten_cli.cli import app
    
    runner = CliRunner()
    result = runner.invoke(app, ["model", "list"])
    
    assert result.exit_code == 0
    
    # Check that all expected models are listed
    expected_models = ["mini", "micro", "nano", "nano-int8"]
    for model in expected_models:
        assert model in result.stdout
    
    # Check that status indicators are present
    assert "[installed]" in result.stdout or "[not installed]" in result.stdout


def test_model_install_unknown_model():
    """Test the 'purr model install' command with unknown model."""
    from kitten_cli.cli import app
    
    runner = CliRunner()
    result = runner.invoke(app, ["model", "install", "unknown-model"])
    
    assert result.exit_code == 1
    # Typer echoes to stderr by default
    assert "Unknown model alias 'unknown-model'" in result.stderr


def test_model_remove_unknown_model():
    """Test the 'purr model remove' command with unknown model."""
    from kitten_cli.cli import app
    
    runner = CliRunner()
    result = runner.invoke(app, ["model", "remove", "unknown-model"])
    
    assert result.exit_code == 1
    # Typer echoes to stderr by default
    assert "Unknown model alias 'unknown-model'" in result.stderr


def test_speak_command_unknown_model():
    """Test the 'purr speak' command with unknown model."""
    from kitten_cli.cli import app
    
    runner = CliRunner()
    result = runner.invoke(app, ["speak", "Hello", "--model", "unknown-model"])
    
    assert result.exit_code == 1
    # Typer echoes to stderr by default
    assert "Unknown model alias 'unknown-model'" in result.stderr


def test_speak_command_no_text():
    """Test the 'purr speak' command with no text provided."""
    from kitten_cli.cli import app
    
    runner = CliRunner()
    result = runner.invoke(app, ["speak"])
    
    assert result.exit_code == 1
    # Typer echoes to stderr by default
    # In test environment, stdin is not a TTY, so it reads empty input and shows "Empty input"
    assert "Empty input" in result.stderr


def test_speak_command_empty_text():
    """Test the 'purr speak' command with empty text."""
    from kitten_cli.cli import app
    
    runner = CliRunner()
    result = runner.invoke(app, ["speak", ""])
    
    assert result.exit_code == 1
    # Typer echoes to stderr by default
    assert "Empty input" in result.stderr


def test_speak_command_invalid_options():
    """Test the 'purr speak' command with invalid option combinations."""
    from kitten_cli.cli import app
    
    runner = CliRunner()
    
    # Test --stdout and --play together
    result = runner.invoke(app, ["speak", "Hello", "--stdout", "--play"])
    assert result.exit_code == 1
    # Typer echoes to stderr by default
    assert "--stdout and --play cannot be used together" in result.stderr
    
    # Test --stdout and --output together
    result = runner.invoke(app, ["speak", "Hello", "--stdout", "--output", "/tmp/test.wav"])
    assert result.exit_code == 1
    # Typer echoes to stderr by default
    assert "--stdout and --output cannot be used together" in result.stderr


def test_voices_command_unknown_model():
    """Test the 'purr voices' command with unknown model."""
    from kitten_cli.cli import app
    
    runner = CliRunner()
    result = runner.invoke(app, ["voices", "--model", "unknown-model"])
    
    assert result.exit_code == 1
    # Typer echoes to stderr by default
    assert "Unknown model alias 'unknown-model'" in result.stderr


def test_voices_command_success(mock_models_dir, installed_model):
    """Test the 'purr voices' command with an installed model."""
    from kitten_cli.cli import app
    
    runner = CliRunner()
    result = runner.invoke(app, ["voices", "--model", installed_model[0]])
    
    assert result.exit_code == 0
    # Mock voices from tests/mock_kittentts.py are Jasper, Luna, Mia, Ryan
    assert "Jasper" in result.stdout
    assert "Luna" in result.stdout


def test_voices_command_auto_install(mock_models_dir):
    """Test 'purr voices' with a non-installed model (should auto-install)."""
    from kitten_cli.cli import app
    
    runner = CliRunner()
    # Use a valid model alias that isn't installed
    result = runner.invoke(app, ["voices", "--model", "nano"])
    
    assert result.exit_code == 0
    assert "Model 'nano' not found locally. Downloading ..." in result.stdout
    assert "Jasper" in result.stdout


def test_speak_command_stdin():
    """Test the 'purr speak' command reading from stdin."""
    from kitten_cli.cli import app
    
    runner = CliRunner()
    # Provide text via input parameter (simulates stdin)
    result = runner.invoke(app, ["speak"], input="Hello from stdin")
    
    assert result.exit_code == 0
    assert "Saved to" in result.stdout


def test_voices_offline_restoration(mock_models_dir, installed_model, monkeypatch):
    """Test that voices command correctly restores HF_HUB_OFFLINE."""
    from kitten_cli.cli import voices
    import os
    
    model_name, _ = installed_model
    monkeypatch.delenv("HF_HUB_OFFLINE", raising=False)
    
    voices(model=model_name)
    assert "HF_HUB_OFFLINE" not in os.environ


def test_speak_command_tty_error():
    """Test the 'purr speak' command when no text is provided and it's a TTY."""
    from kitten_cli.cli import speak
    from unittest.mock import MagicMock, patch
    import typer
    
    # Patch isatty at the module level where it's used
    with patch("kitten_cli.cli.sys.stdin.isatty", return_value=True):
        with pytest.raises(typer.Exit) as exc_info:
            speak(text=None)
        assert exc_info.value.exit_code == 1


def test_model_install_command_success(mock_models_dir):
    """Test the 'purr model install' command."""
    from kitten_cli.cli import app
    
    runner = CliRunner()
    result = runner.invoke(app, ["model", "install", "nano"])
    
    assert result.exit_code == 0
    assert "Model 'nano' installed" in result.stdout


def test_help_command():
    """Test the 'purr --help' command."""
    from kitten_cli.cli import app
    
    runner = CliRunner()
    result = runner.invoke(app, ["--help"])
    
    assert result.exit_code == 0
    assert "purr — KittenTTS CLI for model management and speech synthesis" in result.stdout
    assert "speak" in result.stdout
    assert "model" in result.stdout
    assert "voices" in result.stdout