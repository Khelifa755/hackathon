# Decision Log

- 2026-10-10: Use `config.py` as the single shared configuration source for the initial skeleton; environment variables provide deployment-time overrides without introducing a second config format.
- 2026-10-10: Keep Docker services on one local image and use status commands until stage implementations exist.
- 2026-10-11: Use the pure NumPy/Pillow fallback as the operational simulator when Blender is absent; this keeps the dataset deterministic and runnable without installing Blender. The Blender entry point preserves the same schema and output contract.
