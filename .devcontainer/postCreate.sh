#!/usr/bin/env bash
set -euo pipefail

# Since there are docker volume mounts we need to make sure the cache and venv directories are writable
# by the non-root user
sudo chmod -R 777 /home/vscode/.cache
sudo chmod -R 777 /workspace/.venv

# Might be a small timing issue with the docker mount
uv venv || (sleep 1 && uv venv)
uv run pip install --upgrade pip
uv sync