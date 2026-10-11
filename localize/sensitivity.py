"""Quantify projection sensitivity to slope and camera-height assumptions."""
from __future__ import annotations
import numpy as np
from .projection import CameraModel, project_site_points

def run() -> list[tuple[float, float]]:
    points = np.array([[3., 0.], [6., 1.], [10., -2.]])
    nominal = CameraModel(500., 500., 320., 240., .6, np.deg2rad(15.))
    pixels = project_site_points(points, nominal)
    rows = []
    for slope, height_error in [(0., .05), (np.tan(np.deg2rad(10)), 0.), (np.tan(np.deg2rad(10)), .05)]:
        assumed = CameraModel(500., 500., 320., 240., .6 + height_error, np.deg2rad(15.), slope, 0.)
        estimate, valid = __import__('localize.projection', fromlist=['project_pixels']).project_pixels(pixels, assumed)
        rows.append((slope, float(np.mean(np.linalg.norm(estimate[valid] - points[valid], axis=1)))))
    return rows

if __name__ == '__main__':
    for slope, error in run(): print(f'{slope:.6f} {error:.4f} m')
