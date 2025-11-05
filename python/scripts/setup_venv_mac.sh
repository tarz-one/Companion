#!/usr/bin/env bash
set -e
cd "$(dirname "$0")/.."
python3 -m venv .venv
source .venv/bin/activate
pip install -U pip
pip install -r python/requirements.txt
echo "✅ venv ready. activate with: source python/.venv/bin/activate"
