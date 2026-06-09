from __future__ import annotations

import csv
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from fibcodec.baselines import CODECS
from fibcodec.metrics import compression_metrics, shannon_entropy


def main() -> None:
    rows = []
    for corpus in ("canterbury", "silesia"):
        corpus_root = ROOT / "data" / corpus
        for path in sorted(corpus_root.iterdir()):
            if not path.is_file():
                continue
            data = path.read_bytes()
            h0 = shannon_entropy(data)
            for method, function in CODECS.items():
                start = time.perf_counter()
                compressed = function(data)
                elapsed = time.perf_counter() - start
                metrics = compression_metrics(len(data), len(compressed))
                row = {
                    "corpus": corpus,
                    "file": path.name,
                    "method": method,
                    "original_bytes": len(data),
                    "compressed_bytes": len(compressed),
                    "ratio": metrics["ratio"],
                    "bits_per_byte": metrics["bits_per_byte"],
                    "entropy_bits_per_byte": h0,
                    "gap_to_h0_bits_per_byte": metrics["bits_per_byte"] - h0,
                    "seconds": elapsed,
                    "throughput_mib_s": (
                        len(data) / (1024 * 1024) / elapsed if elapsed else float("inf")
                    ),
                }
                rows.append(row)
                print(corpus, path.name, method, f"ratio={metrics['ratio']:.4f}", flush=True)
    output = ROOT / "results" / "full_baselines.csv"
    with output.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)


if __name__ == "__main__":
    main()

