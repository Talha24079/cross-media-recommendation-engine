#!/usr/bin/env bash
set -euo pipefail

# Usage: run from backend/ folder
# Creates venv, activates, and installs requirements

if [ ! -d "venv" ]; then
  python -m venv venv
fi

# shellcheck source=/dev/null
. venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt

echo "Virtualenv created and dependencies installed. Activate with: source venv/bin/activate"
