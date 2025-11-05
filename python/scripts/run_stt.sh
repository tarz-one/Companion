#!/usr/bin/env bash
set -e
cd "$(dirname "$0")/.."
source .venv/bin/activate || { echo "Run setup_venv_mac.sh first"; exit 1; }
python stt_osc_whisper.py
