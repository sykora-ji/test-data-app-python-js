#!/bin/bash
set -euo pipefail

echo "=== Installing Python dependencies ==="
cd /app
uv sync

echo "=== Installing frontend dependencies ==="
cd /app/frontend
yarn install

echo "=== Building frontend ==="
yarn build

echo "=== Pre-downloading ML models ==="
cd /app
export TRANSFORMERS_CACHE="/tmp/huggingface_cache"
uv run python -c "
from transformers import pipeline
print('Downloading sentiment model...')
pipeline('sentiment-analysis', model='cardiffnlp/twitter-roberta-base-sentiment-latest')
print('Model downloaded successfully.')
"

echo "=== Setup complete ==="
