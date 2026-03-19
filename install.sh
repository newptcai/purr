#!/usr/bin/env bash
# Lean install for purr — avoids the torch/CUDA bloat caused by
# misaki[en] → spacy-curated-transformers → torch.
#
# Strategy: install kittentts and misaki without deps, then supply
# only the deps that are actually needed at runtime.
set -euo pipefail

UV="uv pip install"

# kittentts and its direct deps — skip misaki[en] to avoid torch
$UV --no-deps \
    "kittentts @ https://github.com/KittenML/KittenTTS/releases/download/0.8.1/kittentts-0.8.1-py3-none-any.whl"

# misaki without [en] extra — no spacy-curated-transformers, no torch
$UV --no-deps misaki

# the misaki[en] deps we actually need (espeakng-loader, num2words,
# phonemizer-fork, spacy) — but NOT spacy-curated-transformers
$UV espeakng-loader num2words "phonemizer-fork" spacy

# remaining kittentts deps
$UV onnxruntime soundfile numpy huggingface_hub

# purr itself and its deps
$UV "typer[all]>=0.12" "sounddevice>=0.4"
$UV --no-deps \
    "kitten-cli @ git+https://github.com/newptcai/purr"
