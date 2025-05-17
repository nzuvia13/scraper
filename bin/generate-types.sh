#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
PROJECT_ROOT=$(readlink -f "$SCRIPT_DIR/..")

TARGET_PYTHON_VERSION=3.12

uv run datamodel-codegen  \
    --input "$PROJECT_ROOT/vendored/openapi/sam.gov/get-opportunities-v2.yaml" \
    --input-file-type openapi \
    --output "$PROJECT_ROOT/rfp_scraper/generated/sam_gov_models.py" \
    --strict-nullable \
    --target-python-version="$TARGET_PYTHON_VERSION" \
    --reuse-model \
    --use-field-description \
    --use-union-operator \
    --use-standard-collections \
    --enum-field-as-literal=all \
    --formatters=ruff-check
