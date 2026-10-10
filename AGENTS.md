# UMBRA contribution rules

- Use Python 3.11 and type hints.
- Keep behavior deterministic from `SEED` in `config.py`.
- Keep rover memory bounded with fixed-size buffers and watchdog ticks.
- Do not add cloud APIs, tc/netem, protobuf, or msgpack to the core path.
- Every module needs pytest tests and a benchmark writing to `reports/`.
- Run `make test` before completing work.
- Record ambiguous design decisions in `docs/DECISIONS.md`.
