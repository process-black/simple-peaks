#!/bin/bash
# Activate the Python virtual environment for this project
if [ ! -d ".venv" ]; then
  echo "Virtual environment not found. Run ./setup.sh first."
  exit 1
fi
source .venv/bin/activate
