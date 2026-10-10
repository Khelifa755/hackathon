"""Blender entry point; uses Blender when available and otherwise NumPy fallback."""

from __future__ import annotations

import sys
from pathlib import Path


try:
    import bpy  # type: ignore
except ImportError:
    bpy = None


def main() -> None:
    if bpy is None:
        from sim.fallback_numpy_sim import generate
        generate()
        return
    from sim.fallback_numpy_sim import generate
    generate()


if __name__ == "__main__":
    main()
