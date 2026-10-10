#!/usr/bin/env bash
set -euo pipefail

if command -v blender >/dev/null 2>&1; then
  echo '{"renderer":"blender"}'
  blender -b -P sim/make_traverse.py
else
  echo '{"renderer":"numpy","reason":"blender_not_installed"}'
  python sim/fallback_numpy_sim.py
fi
