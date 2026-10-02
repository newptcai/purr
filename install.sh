#!/usr/bin/env bash
# Install (or reinstall) purr as a uv tool from this source tree.
#
# kittentts is pinned to an upstream commit that no longer depends on
# misaki/spaCy, so no torch/CUDA packages are pulled in and no excludes are needed.
set -euo pipefail

uv tool install --reinstall .
