#!/usr/bin/env bash
# MediTrack Pro — starts Flask backend
set -e

cd "$(dirname "$0")/backend"

# Install dependencies if needed
if ! python3 -c "import flask" 2>/dev/null; then
  echo "Instalando dependencias..."
  pip3 install -r requirements.txt
fi

echo "Iniciando MediTrack Pro en http://localhost:5000"
python3 app.py
