"""Fixed-capacity multi-object tracker in pixel space."""
from __future__ import annotations
from dataclasses import dataclass, field
from collections import Counter
import numpy as np

MAX_TRACKS = 64
@dataclass(frozen=True)
class Detection:
    bbox: np.ndarray
    class_id: int
    score: float = 1.0
@dataclass
class Track:
    track_id: int
    state: np.ndarray
    covariance: np.ndarray
    class_votes: Counter = field(default_factory=Counter)
    hits: int = 1
    misses: int = 0
    age: int = 1
    confirmed: bool = False
    @property
    def bbox(self) -> np.ndarray:
        return self.state[:4].copy()
    @property
    def class_id(self) -> int:
        return self.class_votes.most_common(1)[0][0]

class MultiObjectTracker:
    def __init__(self, max_tracks: int = MAX_TRACKS, iou_threshold: float = 0.05, max_misses: int = 8) -> None:
        self.max_tracks, self.iou_threshold, self.max_misses = min(max_tracks, MAX_TRACKS), iou_threshold, max_misses
        self.tracks: list[Track] = []
        self.next_id = 1
    @staticmethod
    def _iou(a: np.ndarray, b: np.ndarray) -> float:
        x0, y0 = np.maximum(a[:2], b[:2]); x1, y1 = np.minimum(a[2:], b[2:])
        inter = max(0.0, x1-x0) * max(0.0, y1-y0)
        area_a = max(0.0, a[2]-a[0]) * max(0.0, a[3]-a[1])
        area_b = max(0.0, b[2]-b[0]) * max(0.0, b[3]-b[1])
        return inter / max(area_a + area_b - inter, 1e-9)
    def _new(self, d: Detection) -> None:
        if len(self.tracks) >= self.max_tracks: return
        b = np.asarray(d.bbox, dtype=float)
        self.tracks.append(Track(self.next_id, np.r_[b, 0., 0., 0., 0.], np.eye(8)*10., Counter({d.class_id: 1})))
        self.next_id += 1
    def update(self, detections: list[Detection]) -> list[Track]:
        for t in self.tracks:
            t.state[:4] += t.state[4:]
            t.covariance += np.eye(8) * 0.5
            t.age += 1
        pairs: list[tuple[float, int, int]] = []
        for i, t in enumerate(self.tracks):
            for j, d in enumerate(detections):
                pairs.append((self._iou(t.bbox, d.bbox), i, j))
        used_t, used_d = set(), set()
        for score, i, j in sorted(pairs, reverse=True):
            if score < self.iou_threshold or i in used_t or j in used_d: continue
            t, d = self.tracks[i], detections[j]
            residual = np.asarray(d.bbox) - t.state[:4]
            t.state[:4] += 0.65 * residual
            t.state[4:] = 0.35 * t.state[4:] + 0.65 * residual
            t.covariance *= 0.7; t.class_votes[d.class_id] += 1; t.hits += 1; t.misses = 0
            t.confirmed = t.confirmed or t.hits >= 3
            used_t.add(i); used_d.add(j)
        for i, t in enumerate(self.tracks):
            if i not in used_t: t.misses += 1
        self.tracks = [t for t in self.tracks if t.misses < self.max_misses]
        for j, d in enumerate(detections):
            if j not in used_d: self._new(d)
        return list(self.tracks)
