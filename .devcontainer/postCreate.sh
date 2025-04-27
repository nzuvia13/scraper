#!/usr/bin/env bash
set -euo pipefail

uv venv
uv run pip install --upgrade pip
uv sync