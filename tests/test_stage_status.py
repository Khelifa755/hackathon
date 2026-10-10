import subprocess
import sys


EXPECTED = ["sim", "perceive", "localize", "encode", "link", "ground", "dashboard"]


def test_stage_status_lists_all_stages():
    result = subprocess.run(
        [sys.executable, "scripts/stage_status.py"],
        check=True,
        capture_output=True,
        text=True,
    )
    assert result.stdout.splitlines() == [
        f"stage {stage}: not implemented" for stage in EXPECTED
    ]
