"""Remove generated benchmark and Python cache files."""

from pathlib import Path


for path in Path("reports").glob("*"):
    if path.is_file():
        path.unlink()
for path in Path(".").rglob("__pycache__"):
    if path.is_dir():
        for child in path.iterdir():
            if child.is_file():
                child.unlink()
        path.rmdir()
