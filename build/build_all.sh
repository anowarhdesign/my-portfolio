#!/usr/bin/env bash
# Regenerate every page. Run from anywhere: build/build_all.sh
set -euo pipefail
cd "$(dirname "$0")"
python3 pages.py && python3 pages2.py && python3 pages3.py
echo "Built. Serve with: python3 -m http.server 8000 --directory .."
