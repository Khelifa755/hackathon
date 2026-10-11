"""Seeded dead-reckoning odometry and SE(2) transforms."""
from __future__ import annotations
from dataclasses import dataclass
import numpy as np

@dataclass
class PoseEstimate:
    pose: np.ndarray
    covariance: np.ndarray

class OdometryEstimator:
    def __init__(self, seed: int = 26, dt: float = 0.1, drift: bool = True) -> None:
        self.rng = np.random.default_rng(seed); self.dt = dt; self.drift = drift
        self.pose = np.zeros(3); self.bias = np.zeros(2); self.covariance = np.zeros((3, 3))
    def update(self, true_pose: np.ndarray, previous_true: np.ndarray | None = None) -> PoseEstimate:
        if previous_true is None: previous_true = true_pose
        delta = np.asarray(true_pose) - np.asarray(previous_true)
        delta[2] = np.arctan2(np.sin(delta[2]), np.cos(delta[2]))
        if self.drift: self.bias += self.rng.normal(0.0, [0.0008, 0.00015])
        measurement = delta + self.bias * self.dt + self.rng.normal(0.0, [0.008, 0.0015, 0.0008])
        c, s = np.cos(self.pose[2]), np.sin(self.pose[2])
        self.pose[:2] += np.array([[c, -s], [s, c]]) @ measurement[:2]
        self.pose[2] += measurement[2]
        q = np.diag([0.008**2, 0.008**2, 0.0015**2])
        self.covariance += q + np.diag([0.00002, 0.00002, 0.000002])
        return PoseEstimate(self.pose.copy(), self.covariance.copy())

def rover_to_site(points: np.ndarray, pose: np.ndarray) -> np.ndarray:
    p = np.asarray(points, dtype=float).reshape(-1, 2); c, s = np.cos(pose[2]), np.sin(pose[2])
    return p @ np.array([[c, s], [-s, c]]) + pose[:2]

def site_to_rover(points: np.ndarray, pose: np.ndarray) -> np.ndarray:
    p = np.asarray(points, dtype=float).reshape(-1, 2) - pose[:2]; c, s = np.cos(pose[2]), np.sin(pose[2])
    return p @ np.array([[c, -s], [s, c]])
