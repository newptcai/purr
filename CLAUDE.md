# kitten-cli dev notes

## Local setup

```bash
uv venv
source .venv/bin/activate
bash install.sh          # lean install — no torch/CUDA bloat
uv pip install -e .      # install purr itself in editable mode
```

`install.sh` installs kittentts and its deps manually, skipping `spacy-curated-transformers`
which is the transitive source of torch. Then `-e .` wires up the local source.

## Running tests

```bash
pytest tests/
```

Tests mock out `kittentts`, `sounddevice`, and `soundfile` — no model download or audio hardware needed.

## Manual smoke test

```bash
purr model list
purr model install nano
purr speak "Hello, world." --output /tmp/test.wav
purr speak "Hello, world."                         # auto /tmp/purr-<ts>.wav
purr speak "Hello, world." --play
echo "Testing stdin" | purr speak --play --voice Luna
purr voices --model nano
purr model remove nano
```

Model files land in `~/.cache/kitten-cli/models/nano/`.
