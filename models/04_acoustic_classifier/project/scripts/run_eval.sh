#!/usr/bin/env bash
set -euo pipefail

python src/infer.py --config configs/default.yaml
python src/evaluate.py --config configs/default.yaml
