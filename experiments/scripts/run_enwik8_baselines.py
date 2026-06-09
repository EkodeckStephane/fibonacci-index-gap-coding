from __future__ import annotations

import csv
import hashlib
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from fibcodec.baselines import CODECS
from fibcodec.metrics import compression_metrics


def main() -> None:
    path = ROOT / "data" / "enwik8" / "enwik8"
    data = path.read_bytes()
    digest = hashlib.sha256(data).hexdigest()
    rows = []
    for method, function in CODECS.items():
        start = time.perf_counter()
        compressed = function(data)
        elapsed = time.perf_counter() - start
        metrics = compression_metrics(len(data), len(compressed))
        rows.append(
            {
                "corpus": "enwik8",
                "file": path.name,
                "sha256": digest,
                "method": method,
                "original_bytes": len(data),
                "compressed_bytes": len(compressed),
                "ratio": metrics["ratio"],
                "bits_per_byte": metrics["bits_per_byte"],
                "seconds": elapsed,
                "throughput_mib_s": len(data) / (1024 * 1024) / elapsed,
            }
        )
        print(method, f"ratio={metrics['ratio']:.4f}", flush=True)
    with (ROOT / "results" / "enwik8_baselines.csv").open(
        "w", newline="", encoding="utf-8"
    ) as handle:
        writer = csv.DictWriter(handle, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)


if __name__ == "__main__":
    main()
