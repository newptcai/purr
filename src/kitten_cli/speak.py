import os
import time
from pathlib import Path
from typing import Optional

import soundfile as sf
import typer
from kittentts import KittenTTS  # type: ignore

from kitten_cli.config import DEFAULT_MODEL, DEFAULT_SPEED, DEFAULT_VOICE, MODELS_DIR, MODEL_REGISTRY, SAMPLE_RATE
from kitten_cli.models import install_model, is_model_downloaded


def synthesize(
    text: str,
    model: str = DEFAULT_MODEL,
    voice: str = DEFAULT_VOICE,
    speed: float = DEFAULT_SPEED,
    output: Optional[Path] = None,
    play: bool = False,
    clean: bool = True,
) -> Path:
    if model not in MODEL_REGISTRY:
        typer.echo(
            f"Unknown model alias '{model}'. Available: {', '.join(MODEL_REGISTRY)}",
            err=True,
        )
        raise typer.Exit(1)

    if not is_model_downloaded(model):
        typer.echo(f"Model '{model}' not found locally. Downloading ...")
        install_model(model)

    if output is None:
        ts = int(time.time())
        output = Path(f"/tmp/purr-{ts}.wav")

    model_dir = MODELS_DIR / model
    repo_id = MODEL_REGISTRY[model]
    os.environ["HF_HUB_OFFLINE"] = "1"
    tts = KittenTTS(repo_id, cache_dir=str(model_dir))
    del os.environ["HF_HUB_OFFLINE"]

    audio = tts.generate(text, voice=voice, speed=speed, clean_text=clean)

    sf.write(str(output), audio, SAMPLE_RATE)
    typer.echo(f"Saved to {output}")

    if play:
        from kitten_cli.playback import play_audio_array
        play_audio_array(audio, SAMPLE_RATE)

    return output
