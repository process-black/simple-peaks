#!/bin/bash
set -e

# 1. Create venv if not already present
if [ ! -d ".venv" ]; then
  python3 -m venv .venv
fi

# 2. Activate venv
source .venv/bin/activate

# 3. Upgrade pip
pip install --upgrade pip

# 4. Install project in editable mode
pip install -e .

# 5. Optionally install dev dependencies
if [ -f requirements-dev.txt ]; then
  pip install -r requirements-dev.txt
fi

# 6. Check for ffmpeg
if ! command -v ffmpeg &> /dev/null; then
  echo "Warning: ffmpeg is not installed or not in PATH. Please install ffmpeg for full functionality."
fi

echo "Setup complete. To activate the venv in the future, run:"
echo "  source .venv/bin/activate"