# purr

A CLI wrapper for [KittenTTS](https://github.com/KittenML/KittenTTS) — lightweight ONNX-based
text-to-speech on CPU, with model management and optional audio playback.

## Installation

> **Note:** Linux only. Requires Python ≥ 3.8.

### Recommended: lean install (no torch/CUDA)

The default install pulls `torch` and NVIDIA CUDA packages (several GB) as an unnecessary
side-effect of `kittentts → misaki[en] → spacy-curated-transformers`. Use the provided script
to bypass this:

```bash
git clone https://github.com/newptcai/purr
cd purr
uv venv && source .venv/bin/activate
bash install.sh
```

### Simple install (includes torch/CUDA bloat)

```bash
uv venv && source .venv/bin/activate
uv pip install git+https://github.com/newptcai/purr
```

## Quick Start

```bash
# List available models
purr model list

# Download the nano model (~50 MB)
purr model install nano

# Synthesize speech to a file
purr speak "Hello, world." --output hello.wav

# Play audio immediately (saves to /tmp/purr-<timestamp>.wav)
purr speak "Hello, world." --play

# Pipe text from stdin
echo "Testing stdin input" | purr speak --play --voice Luna

# List voices for the active model
purr voices
```

## Commands

### `purr model`

| Command | Description |
|---|---|
| `purr model list` | Show all models with installation status |
| `purr model install <alias>` | Download and install a model |
| `purr model remove <alias>` | Remove an installed model |

Available model aliases: `mini`, `micro`, `nano`, `nano-int8`

### `purr speak`

```
purr speak [TEXT] [OPTIONS]
```

| Option | Short | Default | Description |
|---|---|---|---|
| `--model` | `-m` | `nano` | Model alias |
| `--voice` | `-V` | `Jasper` | Voice name |
| `--speed` | `-s` | `1.0` | Speed multiplier |
| `--output` | `-o` | `/tmp/purr-<ts>.wav` | Output `.wav` file |
| `--play` / `--no-play` | `-p` | off | Play audio after synthesis |
| `--clean` / `--no-clean` | | on | Text preprocessing |

If `TEXT` is omitted, input is read from stdin.

### `purr voices`

```
purr voices [--model nano]
```

Lists available voices for the specified model.

## Model Cache

Models are stored in `~/.cache/kitten-cli/models/` by default.
Respects `$XDG_CACHE_HOME` if set.

## License

MIT
