.PHONY: setup demo test bench docker clean lint

setup:
	python -m pip install -e ".[dev]"

demo:
	@python scripts/stage_status.py

test:
	python -m pytest

bench:
	@python scripts/stage_status.py --bench

docker:
	docker compose config

clean:
	python scripts/clean.py

lint:
	python -m ruff check .
