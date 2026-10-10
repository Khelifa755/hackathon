"""Print the current implementation status of each pipeline stage."""

from __future__ import annotations

import argparse

STAGES = ("sim", "perceive", "localize", "encode", "link", "ground", "dashboard")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--bench", action="store_true")
    args = parser.parse_args()
    for stage in STAGES:
        print(f"stage {stage}: not implemented")
