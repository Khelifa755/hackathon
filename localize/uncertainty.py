"""Analytic first-order uncertainty propagation."""
from __future__ import annotations
import numpy as np
from .projection import CameraModel, projection_jacobian

def propagate(pixel: np.ndarray, pixel_sigma: float, camera: CameraModel, pose: np.ndarray, pose_covariance: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    from .projection import project_pixels
    rover, valid = project_pixels(np.asarray(pixel)[None], camera)
    if not valid[0]: raise ValueError("invalid ground intersection")
    j_pixel = projection_jacobian(pixel, camera)
    c, s = np.cos(pose[2]), np.sin(pose[2]); r = np.array([[c, -s], [s, c]])
    site = rover @ r.T + pose[:2]
    j_pose = np.array([[1., 0., -s * rover[0, 0] - c * rover[0, 1]], [0., 1., c * rover[0, 0] - s * rover[0, 1]]])
    covariance = r @ (j_pixel @ j_pixel.T * pixel_sigma**2) @ r.T + j_pose @ pose_covariance @ j_pose.T
    covariance = (covariance + covariance.T) / 2
    return site[0], covariance

def ellipse(covariance: np.ndarray) -> tuple[float, float, float, float]:
    values, vectors = np.linalg.eigh((covariance + covariance.T) / 2); order = np.argsort(values)[::-1]
    values, vectors = np.maximum(values[order], 0), vectors[:, order]
    return float(np.sqrt(values[0])), float(np.sqrt(values[1])), float(np.arctan2(vectors[1, 0], vectors[0, 0])), float(np.sqrt(values[0]))
