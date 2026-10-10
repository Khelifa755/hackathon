"""Fast deterministic NumPy renderer for the UMBRA traverse dataset."""

from __future__ import annotations

import hashlib
import json
import math
import os
import shutil
from pathlib import Path
from typing import Any

import numpy as np

WIDTH, HEIGHT, FPS, FRAME_COUNT = 640, 480, 10, 900
FX, FY, CX, CY = 500.0, 500.0, WIDTH / 2.0, HEIGHT / 2.0
CLASSES = {"rock": 0, "crater": 1, "ice": 2}
COLORS = {0: (105, 112, 121), 1: (66, 48, 38), 2: (235, 245, 250)}


def _rng(seed: int) -> np.random.Generator:
    return np.random.default_rng(seed)


def _pose(frame: int) -> tuple[float, float, float]:
    t = frame / FPS
    x = 0.5 * t
    y = 3.0 * math.sin(x / 7.5)
    yaw = math.atan2(0.5 * 3.0 / 7.5 * math.cos(x / 7.5), 0.5)
    return x, y, yaw


def _rotate_to_camera(dx: float, dy: float, yaw: float) -> tuple[float, float]:
    forward = dx * math.cos(yaw) + dy * math.sin(yaw)
    left = -dx * math.sin(yaw) + dy * math.cos(yaw)
    return forward, left


def project_point(x: float, y: float, pose: dict[str, float]) -> tuple[float, float] | None:
    forward, left = _rotate_to_camera(x - pose["x_m"], y - pose["y_m"], pose["yaw_rad"])
    if forward <= 0.5:
        return None
    z = 0.6 * 1.0
    return CX + FX * left / forward, CY + FY * z / forward


def _make_hazards(seed: int) -> list[dict[str, Any]]:
    rng = _rng(seed)
    hazards: list[dict[str, Any]] = []
    specs = [("rock", 40), ("crater", 6), ("ice", 4)]
    for kind, count in specs:
        for _ in range(count):
            for _attempt in range(1000):
                x = float(rng.uniform(2.0, 48.0))
                y = float(rng.uniform(-27.0, 27.0))
                radius = float(rng.uniform(0.35, 0.9) if kind == "rock" else rng.uniform(1.0, 2.0))
                if all(math.hypot(x - h["x_m"], y - h["y_m"]) >= radius + h["radius_m"] + 0.55 for h in hazards):
                    hazards.append({"id": len(hazards), "class": kind, "x_m": round(x, 4), "y_m": round(y, 4), "radius_m": round(radius, 4)})
                    break
    return hazards


def _bbox(hazard: dict[str, Any], pose: dict[str, float]) -> tuple[float, float, float, float] | None:
    forward, left = _rotate_to_camera(hazard["x_m"] - pose["x_m"], hazard["y_m"] - pose["y_m"], pose["yaw_rad"])
    if forward <= 0.6 or forward > 55 or abs(left) > forward * 0.72:
        return None
    radius = hazard["radius_m"]
    u = CX + FX * left / forward
    v = CY + FY * 0.6 / forward
    if not (0.0 <= u < WIDTH and 0.0 <= v < HEIGHT):
        return None
    half_w = FX * radius / forward
    half_h = FY * radius / forward * (1.0 if hazard["class"] != "rock" else 0.8)
    return max(0.0, u - half_w), max(0.0, v - half_h), min(WIDTH - 1.0, u + half_w), min(HEIGHT - 1.0, v + half_h)


def _draw_ellipse(image: np.ndarray, box: tuple[float, float, float, float], color: tuple[int, int, int], seed: int) -> None:
    x0, y0, x1, y1 = [int(v) for v in box]
    x0 = max(0, x0)
    y0 = max(0, y0)
    x1 = min(WIDTH - 1, x1)
    y1 = min(HEIGHT - 1, y1)
    if x1 <= x0 or y1 <= y0:
        return
    yy, xx = np.ogrid[y0 : y1 + 1, x0 : x1 + 1]
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    rx, ry = max(1.0, (x1 - x0) / 2), max(1.0, (y1 - y0) / 2)
    mask = ((xx - cx) / rx) ** 2 + ((yy - cy) / ry) ** 2 <= 1
    patch = image[y0 : y1 + 1, x0 : x1 + 1]
    shade = 0.8 + 0.2 * np.sin((xx + yy + seed) / 13.0)
    for channel, value in enumerate(color):
        values = np.clip(value * shade, 0, 255).astype(np.uint8)
        patch[:, :, channel][mask] = values[mask]


def render_frame(frame: int, hazards: list[dict[str, Any]], pose: dict[str, float], seed: int) -> np.ndarray:
    image = np.zeros((HEIGHT, WIDTH, 3), dtype=np.float32)
    yy = np.arange(HEIGHT, dtype=np.float32)[:, None]
    illumination = 10.0 + 100.0 * np.exp(-((yy - 310.0) / 170.0) ** 2)
    image[:] = illumination[:, :, None]
    image[:, :, 1] *= 1.03
    visible: list[tuple[dict[str, Any], tuple[float, float, float, float]]] = []
    for hazard in hazards:
        box = _bbox(hazard, pose)
        if box is not None:
            visible.append((hazard, box))
    for hazard, box in sorted(visible, key=lambda item: item[1][3], reverse=True):
        x0, y0, x1, y1 = box
        shadow = (x0 + 5, y0 + 4, x1 + 9, y1 + 7)
        _draw_ellipse(image, shadow, (18, 20, 24), seed + frame)
        _draw_ellipse(image, box, COLORS[CLASSES[hazard["class"]]], seed)
        if hazard["class"] == "crater":
            rim = (x0 - 2, y0 - 2, x1 + 2, y1 + 2)
            _draw_ellipse(image, rim, (145, 125, 105), seed)
            _draw_ellipse(image, box, (48, 37, 32), seed)
        elif hazard["class"] == "ice":
            _draw_ellipse(image, box, (245, 250, 255), seed + 4)
    rng = _rng(seed + frame * 7919)
    image += rng.normal(0.0, 2.2, image.shape)
    image = np.clip(image, 0, 255).astype(np.uint8)
    if frame % 137 == 0:
        image = np.clip(image.astype(np.int16) + 35, 0, 255).astype(np.uint8)
    return image


def generate(seed: int | None = None, out_dir: Path | str = Path("sim/out")) -> dict[str, Any]:
    seed = int(os.getenv("SEED", "26")) if seed is None else seed
    out = Path(out_dir)
    if out.exists():
        shutil.rmtree(out)
    frames_dir, labels_dir = out / "frames", out / "labels"
    frames_dir.mkdir(parents=True)
    labels_dir.mkdir()
    hazards = _make_hazards(seed)
    poses: list[dict[str, Any]] = []
    for frame in range(FRAME_COUNT):
        x, y, yaw = _pose(frame)
        pose = {"x_m": x, "y_m": y, "yaw_rad": yaw}
        poses.append({"frame": frame, "t": frame / FPS, **pose})
        image = render_frame(frame, hazards, pose, seed)
        from PIL import Image
        Image.fromarray(image, "RGB").save(frames_dir / f"{frame:06d}.png")
        labels = []
        for hazard in hazards:
            box = _bbox(hazard, pose)
            if box is None:
                continue
            x0, y0, x1, y1 = box
            labels.append(f"{CLASSES[hazard['class']]} {(x0+x1)/2/WIDTH:.6f} {(y0+y1)/2/HEIGHT:.6f} {(x1-x0)/WIDTH:.6f} {(y1-y0)/HEIGHT:.6f}")
        (labels_dir / f"{frame:06d}.txt").write_text("\n".join(labels) + ("\n" if labels else ""), encoding="utf-8")
    truth = {"seed": seed, "fps": FPS, "K": {"fx": FX, "fy": FY, "cx": CX, "cy": CY}, "camera": {"height_m": 0.6, "pitch_deg": 15.0}, "hazards": hazards, "poses": poses, "odometry_noise_model": {"position_sigma_m": 0.02, "yaw_sigma_rad": 0.002, "source": "not applied to truth poses"}}
    (out / "ground_truth.json").write_text(json.dumps(truth, indent=2), encoding="utf-8")
    (out / "classes.yaml").write_text("names:\n  0: rock\n  1: crater\n  2: ice\n", encoding="utf-8")
    (out / "dataset.yaml").write_text("path: .\ntrain: frames\nval: frames\ntest: frames\nnames:\n  0: rock\n  1: crater\n  2: ice\n", encoding="utf-8")
    return truth


if __name__ == "__main__":
    result = generate()
    digest = hashlib.sha256(Path("sim/out/ground_truth.json").read_bytes()).hexdigest()[:12]
    print(json.dumps({"renderer": "numpy", "frames": len(result["poses"]), "hazards": len(result["hazards"]), "truth_sha256": digest}))
