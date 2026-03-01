#!/usr/bin/env bash
set -e

# Moverse a la carpeta raíz del proyecto (proyecto/)
cd "$(dirname "$0")"

# Asegurar que proyecto/ esté en el PYTHONPATH para que "import src" funcione
export PYTHONPATH="$(pwd)"

python scripts/01_download_data.py
python scripts/02_analyze.py
python scripts/03_visualize.py

echo "Pipeline completo ✅"