import numpy as np
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock
import typer
import sys





def test_synthesize_writes_file(tmp_path, mock_models_dir, installed_model):
    """Test that synthesize writes audio to file correctly."""
    from kitten_cli.speak import synthesize
    import soundfile as sf
    
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
    assert audio.shape[0] > 0  # Should have some samples
    assert sample_rate == 24000  # Should use default sample rate





def test_synthesize_unknown_model():
    import typer
    from kitten_cli.speak import synthesize
    
    with pytest.raises(typer.Exit) as exc_info:
        synthesize("hi", model="unknown-model", output=Path("/tmp/x.wav"))
    assert exc_info.value.exit_code == 1


def test_synthesize_empty_text(mock_models_dir, installed_model):
    """Test that synthesize handles empty text (should still generate minimal audio)."""
    from kitten_cli.speak import synthesize
    import soundfile as sf
    
    model_name, model_dir = installed_model
    output = Path("/tmp/empty_test.wav")
    
    # The synthesize function doesn't validate empty text - it just generates minimal audio
    result = synthesize("", model=model_name, output=output, quiet=True)
    
    # Should still succeed and create a file (with minimal audio)
    assert output.exists()
    assert result == output
    
    # Verify the audio file is valid (though very short)
    audio, sample_rate = sf.read(output)
    assert audio.shape[0] >= 0  # May be empty or have minimal samples
    assert sample_rate == 24000


def test_synthesize_different_speeds(tmp_path, mock_models_dir, installed_model):
    """Test that different speed values work correctly."""
    from kitten_cli.speak import synthesize
    import soundfile as sf
    
    model_name, model_dir = installed_model
    text = "Hello world"
    
    # Test normal speed
    output_normal = tmp_path / "normal.wav"
    synthesize(text, model=model_name, speed=1.0, output=output_normal, quiet=True)
    audio_normal, sr_normal = sf.read(output_normal)
    
    # Test faster speed
    output_fast = tmp_path / "fast.wav"
    synthesize(text, model=model_name, speed=2.0, output=output_fast, quiet=True)
    audio_fast, sr_fast = sf.read(output_fast)
    
    # Test slower speed
    output_slow = tmp_path / "slow.wav"
    synthesize(text, model=model_name, speed=0.5, output=output_slow, quiet=True)
    audio_slow, sr_slow = sf.read(output_slow)
    
    # Verify that faster audio is shorter, slower audio is longer
    assert len(audio_fast) < len(audio_normal) < len(audio_slow)
    assert sr_normal == sr_fast == sr_slow == 24000


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


def test_synthesize_auto_output_path(tmp_path, mock_models_dir, installed_model):
    """Test that auto-generated output paths work correctly."""
    from kitten_cli.speak import synthesize
    import re
    
    model_name, model_dir = installed_model
    
    # Test with no output specified (should auto-generate)
    result = synthesize("Test", model=model_name, output=None, quiet=True)
    
    # Verify it returns a Path and the file exists
    assert isinstance(result, Path)
    assert result.exists()
    assert result.name.startswith("purr-")
    assert result.name.endswith(".wav")
    
    # Verify the path format
    assert re.match(r"purr-\d+\.wav", result.name)
