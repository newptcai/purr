import sys
from pathlib import Path
from typing import Optional

import typer

from kitten_cli.config import DEFAULT_MODEL, DEFAULT_SPEED, DEFAULT_VOICE, MODEL_REGISTRY, MODELS_DIR

app = typer.Typer(help="purr — KittenTTS CLI for model management and speech synthesis.")
model_app = typer.Typer(help="Manage KittenTTS models.")
app.add_typer(model_app, name="model")


@model_app.command("list")
def model_list() -> None:
    """List available models and their installation status."""
    from kitten_cli.models import list_models
    list_models()


@model_app.command("install")
def model_install(
    alias: str = typer.Argument(..., help="Model alias: mini | micro | nano | nano-int8"),
) -> None:
    """Download and install a model."""
    from kitten_cli.models import install_model
    install_model(alias)


@model_app.command("remove")
def model_remove(
    alias: str = typer.Argument(..., help="Model alias to remove"),
) -> None:
    """Remove an installed model."""
    from kitten_cli.models import remove_model
    remove_model(alias)


@app.command()
def speak(
    text: Optional[str] = typer.Argument(None, help="Text to synthesize. Reads from stdin if omitted."),
    model: str = typer.Option(DEFAULT_MODEL, "--model", "-m", help="Model alias"),
    voice: str = typer.Option(DEFAULT_VOICE, "--voice", "-V", help="Voice name"),
    speed: float = typer.Option(DEFAULT_SPEED, "--speed", "-s", help="Speed multiplier"),
    output: Optional[Path] = typer.Option(None, "--output", "-o", help="Output .wav file path"),
    play: bool = typer.Option(False, "--play/--no-play", "-p/-P", help="Play audio after generation"),
    stdout: bool = typer.Option(False, "--stdout", help="Write WAV audio to stdout"),
    clean: bool = typer.Option(True, "--clean/--no-clean", help="Apply text preprocessing"),
    quiet: bool = typer.Option(False, "--quiet", "-q", help="Suppress informational output"),
) -> None:
    """Synthesize speech from text or stdin."""
    if stdout and play:
        typer.echo("--stdout and --play cannot be used together.", err=True)
        raise typer.Exit(1)
    if stdout and output is not None:
        typer.echo("--stdout and --output cannot be used together.", err=True)
        raise typer.Exit(1)
    if text is None:
        if sys.stdin.isatty():
            typer.echo("No text provided. Pass text as an argument or pipe via stdin.", err=True)
            raise typer.Exit(1)
        text = sys.stdin.read().strip()

    if not text:
        typer.echo("Empty input.", err=True)
        raise typer.Exit(1)

    from kitten_cli.speak import synthesize
    synthesize(text, model=model, voice=voice, speed=speed, output=output, play=play, stdout=stdout, clean=clean, quiet=quiet)


@app.command()
def voices(
    model: str = typer.Option(DEFAULT_MODEL, "--model", "-m", help="Model alias"),
) -> None:
    """List available voices for a model."""
    if model not in MODEL_REGISTRY:
        typer.echo(
            f"Unknown model alias '{model}'. Available: {', '.join(MODEL_REGISTRY)}",
            err=True,
        )
        raise typer.Exit(1)

    from kittentts import KittenTTS  # type: ignore
    from kitten_cli.models import is_model_downloaded, install_model

    if not is_model_downloaded(model):
        typer.echo(f"Model '{model}' not found locally. Downloading ...")
        install_model(model)

    model_dir = MODELS_DIR / model
    repo_id = MODEL_REGISTRY[model]
    tts = KittenTTS(repo_id, cache_dir=str(model_dir))

    for v in tts.voices():
        typer.echo(f"  {v}")
