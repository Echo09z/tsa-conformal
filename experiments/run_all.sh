#!/usr/bin/env bash
# Regenerates every table and figure in results/ from data/*.npz (about ten minutes on a laptop, most of it b3_kcp.py).
set -euo pipefail
cd "$(dirname "$0")/.."
uv run python experiments/a1_main_calibration.py > /dev/null
uv run python experiments/a2_stratified.py > /dev/null
uv run python experiments/a3_prediction_sets.py > /dev/null
uv run python experiments/a4_calibration_conditional.py > /dev/null
uv run python experiments/b3_kcp.py > /dev/null
uv run python experiments/figures.py > /dev/null
echo "results/ regenerated"
