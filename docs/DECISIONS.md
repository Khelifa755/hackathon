# Decision Log

- 2026-10-10: Use `config.py` as the single shared configuration source for the initial skeleton; environment variables provide deployment-time overrides without introducing a second config format.
- 2026-10-10: Keep Docker services on one local image and use status commands until stage implementations exist.
