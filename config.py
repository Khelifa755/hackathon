"""Shared deterministic configuration for the UMBRA pipeline."""

from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Config:
    seed: int = 26
    rover_port: int = 41001
    link_port: int = 41002
    ground_port: int = 41003
    dashboard_port: int = 8080
    packet_loss: float = 0.20
    duplicate_rate: float = 0.02
    reorder_rate: float = 0.05
    queue_size: int = 256
    watchdog_tick_seconds: float = 0.1


def load_config() -> Config:
    """Load the shared configuration, allowing environment overrides."""
    return Config(
        seed=int(os.getenv("SEED", "26")),
        packet_loss=float(os.getenv("PACKET_LOSS", "0.20")),
        duplicate_rate=float(os.getenv("DUPLICATE_RATE", "0.02")),
        reorder_rate=float(os.getenv("REORDER_RATE", "0.05")),
    )


CONFIG = load_config()
