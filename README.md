# UMBRA

UMBRA is a fully software-emulated pipeline for the ATEC'26 C.R.A.T.E.R. challenge:

`Perceive -> Localize -> Transmit -> Visualize`

## Quickstart

Requirements: Python 3.11, `make`, and optionally Docker Compose.

```bash
make setup
make test
make demo
make bench
```

The initial repository is a contract-first skeleton. Pipeline stages currently report that they are not implemented.

## Architecture

- `sim/`: deterministic video, rover, and scene simulation.
- `perception/`: edge detection and resource measurements.
- `localize/`: projection from detections into site-frame coordinates.
- `codec/`: compact binary telemetry encoding and decoding.
- `transport/`: bounded radio-facing telemetry transport.
- `link_emulator/`: deterministic lossy-link behavior.
- `ground/`: telemetry ingestion and reliability handling.
- `dashboard/`: data-aging and uncertainty visualization.
- `config.py`: the single shared runtime configuration source.
- `docs/`: interface, math, architecture, and decision records.

The real-time path is software-only and uses no cloud services or database. Optional database logging must remain outside the real-time path.

## Results

| Metric | Result | Method |
|---|---:|---|
| | | |

## Space-compliance notes

- Determinism is controlled by the `SEED` environment variable.
- Rover-side queues and buffers must be fixed-size and bounded.
- The rover may use only the radio UDP socket for networking.
- Core telemetry will use an implementation-owned binary codec; JSON and msgpack are benchmark baselines only.
- Projection math, link emulation, and reliability behavior are implemented in-repository.
- Every completed module will include pytest coverage and a benchmark that writes to `reports/`.
