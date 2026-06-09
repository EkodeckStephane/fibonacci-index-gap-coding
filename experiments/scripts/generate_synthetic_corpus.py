from __future__ import annotations

import json
import random
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
CONFIG = json.loads((ROOT / "config" / "experiment.json").read_text(encoding="utf-8"))
OUT = ROOT / "data" / "synthetic"


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    n = int(CONFIG["synthetic_bytes_per_file"])
    seed = int(CONFIG["seed"])
    rng = random.Random(seed)
    np_rng = np.random.default_rng(seed)

    files = {
        "zeros.bin": bytes(n),
        "ones.bin": b"\xff" * n,
        "alternating.bin": (b"\x00\xff" * ((n + 1) // 2))[:n],
        "periodic_text.txt": (
            b"Fibonacci inspired entropy reduction requires exact accounting. "
            * ((n // 65) + 1)
        )[:n],
        "random.bin": rng.randbytes(n),
        "low_alphabet.bin": bytes(np_rng.integers(0, 4, size=n, dtype=np.uint8)),
        "ramp.bin": (bytes(range(256)) * ((n + 255) // 256))[:n],
    }
    for name, payload in files.items():
        (OUT / name).write_bytes(payload)
    print(f"Generated {len(files)} files ({n} bytes each) in {OUT}")


if __name__ == "__main__":
    main()

