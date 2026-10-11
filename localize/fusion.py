"""Static-hazard information-form fusion."""
from __future__ import annotations
from dataclasses import dataclass
import numpy as np

@dataclass
class FusedTrack:
    position: np.ndarray
    covariance: np.ndarray
    n_obs: int
    first_seen: int
    last_seen: int
    class_id: int

class SightingsFusion:
    def __init__(self, gate: float = 9.21) -> None:
        self.tracks: dict[int, FusedTrack] = {}; self.gate = gate
    def update(self, track_id: int, position: np.ndarray, covariance: np.ndarray, frame: int, class_id: int) -> FusedTrack:
        p, r = np.asarray(position, float), np.asarray(covariance, float)
        old = self.tracks.get(track_id)
        if old is None:
            old = FusedTrack(p.copy(), r.copy(), 0, frame, frame, class_id); self.tracks[track_id] = old
        else:
            d = p - old.position; s = old.covariance + r
            if float(d @ np.linalg.pinv(s) @ d) > self.gate: return old
            old_information = np.linalg.pinv(old.covariance)
            measurement_information = np.linalg.pinv(r)
            information = old_information + measurement_information
            old.covariance = np.linalg.pinv(information)
            old.position = old.covariance @ (old_information @ old.position + measurement_information @ p)
        old.n_obs += 1; old.last_seen = frame; old.class_id = class_id
        return old
