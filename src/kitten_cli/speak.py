import contextlib
import io
import os
import sys
import time
from pathlib import Path
from typing import Optional

import soundfile as sf
import typer
from kitten_cli.config import DEFAULT_MODEL, DEFAULT_SPEED, DEFAULT_VOICE, MODELS_DIR, MODEL_REGISTRY, SAMPLE_RATE
from kitten_cli.models import install_model, is_model_downloaded


def synthesize(
    text: str,
    model: str = DEFAULT_MODEL,
    voice: str = DEFAULT_VOICE,
    speed: float = DEFAULT_SPEED,
    output: Optional[Path] = None,
    play: bool = False,
    stdout: bool = False,
    clean: bool = True,
    quiet: bool = False,
) -> Optional[Path]:
    if model not in MODEL_REGISTRY:
        typer.echo(
            f"Unknown model alias '{model}'. Available: {', '.join(MODEL_REGISTRY)}",
            err=True,
        )
        raise typer.Exit(1)

    if not is_model_downloaded(model):
        if not quiet:
            typer.echo(f"Model '{model}' not found locally. Downloading ...")
        install_model(model)

    if stdout:
        quiet = True

    model_dir = MODELS_DIR / model
    repo_id = MODEL_REGISTRY[model]
    os.environ["HF_HUB_OFFLINE"] = "1"
    from kittentts import KittenTTS  # type: ignore  # imported after HF_HUB_OFFLINE is set
    with open(os.devnull, "w") as devnull:
        redirect = contextlib.redirect_stdout(devnull) if quiet else contextlib.nullcontext()
        with redirect:
            tts = KittenTTS(repo_id, cache_dir=str(model_dir))
            audio = tts.generate(text, voice=voice, speed=speed, clean_text=clean)
    del os.environ["HF_HUB_OFFLINE"]

    if stdout:
        buf = io.BytesIO()
        sf.write(buf, audio, SAMPLE_RATE, format="WAV")
        sys.stdout.buffer.write(buf.getvalue())
        return None

    if output is None:
        ts = int(time.time())
        output = Path(f"/tmp/purr-{ts}.wav")

    sf.write(str(output), audio, SAMPLE_RATE)
    if not quiet:
        typer.echo(f"Saved to {output}")

    if play:
        from kitten_cli.playback import play_audio_array
        play_audio_array(audio, SAMPLE_RATE)

    return output
