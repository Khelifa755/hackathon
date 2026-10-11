"""Vectorized pinhole projection from image pixels to ground coordinates."""
from __future__ import annotations
from dataclasses import dataclass
import numpy as np

@dataclass(frozen=True)
class CameraModel:
    fx: float
    fy: float
    cx: float
    cy: float
    height: float
    pitch: float
    slope_x: float = 0.0
    slope_y: float = 0.0

    @property
    def K(self) -> np.ndarray:
        return np.array([[self.fx, 0.0, self.cx], [0.0, self.fy, self.cy], [0.0, 0.0, 1.0]])

def project_pixels(pixels: np.ndarray, camera: CameraModel) -> tuple[np.ndarray, np.ndarray]:
    p = np.asarray(pixels, dtype=float).reshape(-1, 2)
    q = (p[:, 1] - camera.cy) / camera.fy
    l = (p[:, 0] - camera.cx) / camera.fx
    cp, sp = np.cos(camera.pitch), np.sin(camera.pitch)
    forward = cp - sp * q
    down = sp + cp * q
    ground_down = camera.height + camera.slope_x * 0.0 + camera.slope_y * 0.0
    valid = down > 1e-9
    scale = np.divide(ground_down, down, out=np.full_like(down, np.nan), where=valid)
    points = np.column_stack((forward * scale, l * scale))
    if camera.slope_x or camera.slope_y:
        for _ in range(4):
            z = camera.height - camera.slope_x * points[:, 0] - camera.slope_y * points[:, 1]
            scale = np.divide(z, down, out=np.full_like(down, np.nan), where=valid)
            points = np.column_stack((forward * scale, l * scale))
    return points, valid & np.isfinite(points).all(axis=1)

def project_bbox_bottom_center(boxes: np.ndarray, camera: CameraModel) -> tuple[np.ndarray, np.ndarray]:
    b = np.asarray(boxes, dtype=float).reshape(-1, 4)
    return project_pixels(np.column_stack(((b[:, 0] + b[:, 2]) / 2.0, b[:, 3])), camera)

def project_site_points(points: np.ndarray, camera: CameraModel) -> np.ndarray:
    p = np.asarray(points, dtype=float).reshape(-1, 2)
    z = camera.height - camera.slope_x * p[:, 0] - camera.slope_y * p[:, 1]
    cp, sp = np.cos(camera.pitch), np.sin(camera.pitch)
    ratio = z / np.maximum(p[:, 0], 1e-12)
    q = (sp + cp * ratio) / np.maximum(cp - sp * ratio, 1e-12)
    return np.column_stack((camera.cx + camera.fx * p[:, 1] / np.maximum(p[:, 0], 1e-12), camera.cy + camera.fy * q))

def projection_jacobian(pixel: np.ndarray, camera: CameraModel, eps: float = 1e-5) -> np.ndarray:
    p = np.asarray(pixel, dtype=float)
    base, ok = project_pixels(p[None], camera)
    if not ok[0]:
        raise ValueError("ray is above the horizon")
    jac = np.empty((2, 2))
    for i in range(2):
        d = np.zeros(2); d[i] = eps
        plus, _ = project_pixels((p + d)[None], camera)
        minus, _ = project_pixels((p - d)[None], camera)
        jac[:, i] = (plus[0] - minus[0]) / (2 * eps)
    return jac
