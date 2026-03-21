# Speech synthesis module tests for kitten-cli
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock
import typer
import soundfile as sf
import re


def test_synthesize_writes_file(tmp_path, mock_models_dir, installed_model):
    """Test that synthesize writes audio to file correctly."""
    from kitten_cli.speak import synthesize
    
    model_name, model_dir = installed_model
    output = tmp_path / "out.wav"
    
    # Test synthesis with mock model
    result = synthesize(
        "Hello world",
        model=model_name,
        output=output,
        play=False,
        quiet=True,
    )
    
    # Verify file was created
    assert output.exists()
    assert result == output
    
    # Verify audio file is valid
    audio, sample_rate = sf.read(output)
    assert audio.shape[0] > 0
    assert sample_rate == 24000


def test_synthesize_unknown_model(mock_models_dir):
    """Test synthesize with an unknown model alias."""
    from kitten_cli.speak import synthesize
    
    with pytest.raises(typer.Exit) as exc_info:
        synthesize("hi", model="unknown-model", output=Path("/tmp/x.wav"))
    assert exc_info.value.exit_code == 1


def test_synthesize_empty_text(mock_models_dir, installed_model):
    """Test that synthesize handles empty text."""
    from kitten_cli.speak import synthesize
    
    model_name, model_dir = installed_model
    output = Path("/tmp/empty_test.wav")
    
    result = synthesize("", model=model_name, output=output, quiet=True)
    
    assert output.exists()
    assert result == output
    
    audio, sample_rate = sf.read(output)
    assert audio.shape[0] >= 0
    assert sample_rate == 24000


def test_synthesize_different_speeds(tmp_path, mock_models_dir, installed_model):
    """Test that different speed values work correctly."""
    from kitten_cli.speak import synthesize
    
    model_name, model_dir = installed_model
    text = "Hello world"
    
    # Test normal speed
    output_normal = tmp_path / "normal.wav"
    synthesize(text, model=model_name, speed=1.0, output=output_normal, quiet=True)
    audio_normal, _ = sf.read(output_normal)
    
    # Test faster speed
    output_fast = tmp_path / "fast.wav"
    synthesize(text, model=model_name, speed=2.0, output=output_fast, quiet=True)
    audio_fast, _ = sf.read(output_fast)
    
    # Test slower speed
    output_slow = tmp_path / "slow.wav"
    synthesize(text, model=model_name, speed=0.5, output=output_slow, quiet=True)
    audio_slow, _ = sf.read(output_slow)
    
    # Verify that faster audio is shorter, slower audio is longer
    assert len(audio_fast) < len(audio_normal) < len(audio_slow)


def test_synthesize_different_voices(tmp_path, mock_models_dir, installed_model):
    """Test that different voices work correctly."""
    from kitten_cli.speak import synthesize
    
    model_name, model_dir = installed_model
    
    # Test different voices
    for voice in ["Jasper", "Luna", "Mia"]:
        output = tmp_path / f"{voice}.wav"
        result = synthesize("Hello", model=model_name, voice=voice, output=output, quiet=True)
        assert output.exists()
        assert result == output


def test_synthesize_stdout(mock_models_dir, installed_model):
    """Test that synthesize with stdout=True writes WAV to stdout."""
    from kitten_cli.speak import synthesize
    import io
    import sys
    from unittest.mock import MagicMock, patch
    
    model_name, _ = installed_model
    
    # Mock sys.stdout.buffer using patch instead of monkeypatch
    mock_stdout = MagicMock()
    fake_buffer = io.BytesIO()
    mock_stdout.buffer = fake_buffer
    
    with patch("sys.stdout", mock_stdout):
        # Run synthesize with stdout=True
        result = synthesize("Hello world", model=model_name, stdout=True)
        
        # Verify result is None
        assert result is None
        
        # Verify WAV header in stdout
        wav_bytes = fake_buffer.getvalue()
        assert len(wav_bytes) > 0
        assert wav_bytes[:4] == b"RIFF"


def test_synthesize_auto_install(mock_models_dir):
    """Test that synthesize auto-installs missing models."""
    from kitten_cli.speak import synthesize
    
    # Model 'nano' is not installed
    output = Path("/tmp/auto_install.wav")
    
    # Run synthesize (should trigger auto-install)
    result = synthesize("Auto install test", model="nano", output=output, quiet=False)
    
    # Verify model was installed and file created
    assert result == output
    assert (mock_models_dir / "nano").exists()


def test_synthesize_play(mock_models_dir, installed_model):
    """Test that synthesize with play=True calls playback module."""
    from kitten_cli.speak import synthesize
    from unittest.mock import patch
    
    model_name, _ = installed_model
    output = Path("/tmp/play_test.wav")
    
    # Patch the playback module
    with patch("kitten_cli.playback.play_audio_array") as mock_play:
        synthesize("Play me", model=model_name, output=output, play=True, quiet=True)
        
        # Verify play was called
        mock_play.assert_called_once()


def test_synthesize_offline_restoration(mock_models_dir, installed_model, monkeypatch):
    """Test that HF_HUB_OFFLINE is correctly removed if it was not present."""
    from kitten_cli.speak import synthesize
    import os
    
    model_name, _ = installed_model
    monkeypatch.delenv("HF_HUB_OFFLINE", raising=False)
    
    synthesize("test", model=model_name, quiet=True)
    assert "HF_HUB_OFFLINE" not in os.environ


def test_synthesize_auto_output_path(tmp_path, mock_models_dir, installed_model):
    """Test that auto-generated output paths work correctly."""
    from kitten_cli.speak import synthesize
    
    model_name, model_dir = installed_model
    
    # Test with no output specified (should auto-generate)
    result = synthesize("Test", model=model_name, output=None, quiet=True)
    
    # Verify it returns a Path and the file exists
    assert isinstance(result, Path)
    assert result.exists()
    assert result.name.startswith("purr-")
    assert result.name.endswith(".wav")
    assert re.match(r"purr-\d+\.wav", result.name)
