import hashlib
import json
from pathlib import Path

from sim.fallback_numpy_sim import FRAME_COUNT, HEIGHT, WIDTH, _bbox, generate


OUT = Path("sim/out")


def test_sim_schema_and_outputs(tmp_path):
    truth = generate(seed=101, out_dir=tmp_path / "out")
    assert set(truth) == {"seed", "fps", "K", "camera", "hazards", "poses", "odometry_noise_model"}
    assert len(truth["poses"]) == FRAME_COUNT
    assert len(truth["hazards"]) == 50
    assert truth["K"] == {"fx": 500.0, "fy": 500.0, "cx": WIDTH / 2, "cy": HEIGHT / 2}
    assert len(list((tmp_path / "out" / "frames").glob("*.png"))) == FRAME_COUNT
    assert len(list((tmp_path / "out" / "labels").glob("*.txt"))) == FRAME_COUNT


def test_true_projection_lands_in_boxes(tmp_path):
    truth = generate(seed=102, out_dir=tmp_path / "out")
    visible = passed = 0
    for pose in truth["poses"]:
        for hazard in truth["hazards"]:
            box = _bbox(hazard, pose)
            if box is None:
                continue
            visible += 1
            x0, y0, x1, y1 = box
            forward = ((hazard["x_m"] - pose["x_m"]) * __import__("math").cos(pose["yaw_rad"]) + (hazard["y_m"] - pose["y_m"]) * __import__("math").sin(pose["yaw_rad"]))
            left = (-(hazard["x_m"] - pose["x_m"]) * __import__("math").sin(pose["yaw_rad"]) + (hazard["y_m"] - pose["y_m"]) * __import__("math").cos(pose["yaw_rad"]))
            u = truth["K"]["cx"] + truth["K"]["fx"] * left / forward
            v = truth["K"]["cy"] + truth["K"]["fy"] * 0.6 / forward
            passed += int(x0 - 5 <= u <= x1 + 5 and y0 - 5 <= v <= y1 + 5)
    assert visible > 0
    assert passed / visible >= 0.95


def test_sim_is_deterministic(tmp_path):
    first = generate(seed=103, out_dir=tmp_path / "first")
    second = generate(seed=103, out_dir=tmp_path / "second")
    first_hash = hashlib.sha256((tmp_path / "first" / "ground_truth.json").read_bytes()).hexdigest()
    second_hash = hashlib.sha256((tmp_path / "second" / "ground_truth.json").read_bytes()).hexdigest()
    assert first_hash == second_hash
    assert json.dumps(first, sort_keys=True) == json.dumps(second, sort_keys=True)
