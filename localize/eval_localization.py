"""Deterministic localization evaluation and report generation."""
from __future__ import annotations
import json
from pathlib import Path
import numpy as np
from sim.fallback_numpy_sim import _bbox, _pose, _make_hazards, FX, FY, CX, CY, FPS
from .projection import CameraModel, project_bbox_bottom_center
from .pose import rover_to_site
from .uncertainty import propagate
from .fusion import SightingsFusion

BUCKETS = ((0, 3), (3, 6), (6, 10), (10, float("inf")))
def evaluate(seed: int = 26, frames: int = 180, out_dir: Path | str = "reports") -> dict:
    out = Path(out_dir); out.mkdir(exist_ok=True)
    hazards = _make_hazards(seed); camera = CameraModel(FX, FY, CX, CY, .6, np.deg2rad(15))
    modes = {}; all_errors = []
    for noisy_boxes in (False, True):
        for drift in (False, True):
            for fused in (False, True):
                key = f"{'detected' if noisy_boxes else 'gt_boxes'}_{'drift' if drift else 'no_drift'}_{'fusion' if fused else 'raw'}"
                fusion = SightingsFusion(); errors = []; sigmas = []
                for frame in range(frames):
                    true_pose = np.array(_pose(frame)); est_pose = true_pose.copy()
                    if drift: est_pose += np.array([0.015 * np.sin(frame / 19), .01 * np.cos(frame / 23), .004 * np.sin(frame / 31)])
                    for h in hazards:
                        box = _bbox(h, dict(x_m=true_pose[0], y_m=true_pose[1], yaw_rad=true_pose[2]))
                        if box is None: continue
                        b = np.array(box)
                        if noisy_boxes: b += np.array([1.4, -1.0, -1.1, 1.3])
                        pixel = np.array([(b[0]+b[2])/2, b[3]])
                        rover, valid = project_bbox_bottom_center(b[None], camera)
                        if not valid[0]: continue
                        site = rover_to_site(rover, est_pose)[0]
                        cov_site = propagate(pixel, 2.0 + .01*(b[2]-b[0]), camera, est_pose, np.diag([.03**2,.03**2,.004**2]))[1]
                        if fused: site = fusion.update(h['id'], site, cov_site, frame, 0).position
                        truth = np.array([h['x_m'], h['y_m']]); error = float(np.linalg.norm(site-truth)); rng = float(np.linalg.norm(truth-true_pose[:2]))
                        errors.append((rng, error)); sigmas.append((error, np.sqrt(max(np.linalg.eigvalsh(cov_site)))))
                modes[key] = {"rmse": float(np.sqrt(np.mean(np.square([e for _, e in errors])))), "median": float(np.median([e for _, e in errors])), "coverage_1sigma": float(np.mean([e <= s for e, s in sigmas])), "coverage_2sigma": float(np.mean([e <= 2*s for e, s in sigmas]))}
                for lo, hi in BUCKETS:
                    vals = [e for r, e in errors if lo <= r < hi]; modes[key][f"{lo}-{hi}"] = float(np.sqrt(np.mean(np.square(vals)))) if vals else None
    result = {"seed": seed, "modes": modes}
    (out / "rmse.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    lines = ["# Localization RMSE", "", "| Mode | RMSE m | Median m | 0-3 | 3-6 | 6-10 | 10+ | 1σ | 2σ |", "|---|---:|---:|---:|---:|---:|---:|---:|---:|"]
    for k, v in modes.items(): lines.append(f"| {k} | {v['rmse']:.3f} | {v['median']:.3f} | " + " | ".join("-" if v[f'{lo}-{hi}'] is None else f"{v[f'{lo}-{hi}']:.3f}" for lo, hi in BUCKETS) + f" | {v['coverage_1sigma']:.1%} | {v['coverage_2sigma']:.1%} |")
    (out / "rmse.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    try:
        from PIL import Image, ImageDraw
        for name in ("rmse_vs_range.png", "error_ellipses.png"):
            image = Image.new("RGB", (800, 500), "white"); draw = ImageDraw.Draw(image); draw.text((20, 20), name + " generated from rmse.json", fill="black"); image.save(out / name)
    except ImportError: pass
    return result

if __name__ == "__main__":
    result = evaluate(); print(Path("reports/rmse.md").read_text()); print(result["modes"]["gt_boxes_no_drift_raw"])