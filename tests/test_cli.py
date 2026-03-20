# CLI command tests for kitten-cli
import pytest
from pathlib import Path
from typer.testing import CliRunner


def test_model_list_command():
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