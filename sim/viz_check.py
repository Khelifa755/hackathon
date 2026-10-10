"""Create a true-box montage for a quick visual simulation check."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

from sim.fallback_numpy_sim import HEIGHT, WIDTH, _bbox


def main() -> None:
    out = Path("sim/out")
    truth = json.loads((out / "ground_truth.json").read_text(encoding="utf-8"))
    frames = []
    for frame in np.linspace(0, len(truth["poses"]) - 1, 12, dtype=int):
        image = Image.open(out / "frames" / f"{frame:06d}.png").convert("RGB")
        draw = ImageDraw.Draw(image)
        pose = truth["poses"][frame]
        for hazard in truth["hazards"]:
            box = _bbox(hazard, pose)
            if box and box[2] > box[0] and box[3] > box[1]:
                draw.rectangle(box, outline=(255, 40, 40), width=2)
                draw.text((box[0], max(0, box[1] - 12)), str(hazard["id"]), fill=(255, 255, 0))
        frames.append(image.resize((WIDTH // 2, HEIGHT // 2)))
    montage = Image.new("RGB", (WIDTH * 2, HEIGHT * 3 // 2), (0, 0, 0))
    for index, image in enumerate(frames):
        montage.paste(image, ((index % 4) * WIDTH // 2, (index // 4) * HEIGHT // 2))
    Path("reports").mkdir(exist_ok=True)
    montage.save("reports/sim_preview.png")


if __name__ == "__main__":
    main()
