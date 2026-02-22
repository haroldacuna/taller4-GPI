set -e

python -m pip install -r requirements.txt 2>/dev/null || true

python scripts/01_generate_data.py
python scripts/02_analyze.py
python scripts/03_visualize.py

echo "Pipeline completo ✅"