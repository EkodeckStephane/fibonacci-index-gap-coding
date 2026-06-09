from __future__ import annotations

import argparse
import csv
import json
import platform
import statistics
import sys
import time
import tracemalloc
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from fibcodec.baselines import CODECS
from fibcodec.codec import decode, encode
from fibcodec.metrics import compression_metrics, shannon_entropy


def timed_call(function, data: bytes, repetitions: int, warmups: int):
    for _ in range(warmups):
        function(data)
    timings = []
    result = b""
    peak = 0
    for _ in range(repetitions):
        tracemalloc.start()
        start = time.perf_counter_ns()
        result = function(data)
        elapsed = time.perf_counter_ns() - start
        _, current_peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        timings.append(elapsed / 1e9)
        peak = max(peak, current_peak)
    return result, statistics.median(timings), peak


def iter_files(roots: list[str]):
    for root_text in roots:
        root = Path(root_text).resolve()
        if not root.exists():
            continue
        for path in sorted(root.rglob("*")):
            if path.is_file():
                yield root.name, path


def main(config_path: Path) -> None:
    config = json.loads(config_path.read_text(encoding="utf-8"))
    rows = []
    output = Path(config["output_csv"]).resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "corpus",
        "file",
        "method",
        "original_bytes",
        "compressed_bytes",
        "ratio",
        "saving_fraction",
        "bits_per_byte",
        "entropy_bits_per_byte",
        "gap_to_h0_bits_per_byte",
        "median_seconds",
        "throughput_mib_s",
        "peak_tracemalloc_bytes",
    ]
    handle = output.open("w", newline="", encoding="utf-8")
    writer = csv.DictWriter(handle, fieldnames=fieldnames)
    writer.writeheader()
    handle.flush()
    try:
        for corpus, path in iter_files(config["corpus_roots"]):
            data = path.read_bytes()
            entropy = shannon_entropy(data)
            methods = dict(CODECS)
            for block_size in config["block_sizes"]:
                methods[f"fipb_raw_fallback_bs{block_size}"] = (
                    lambda payload, bs=block_size: encode(payload, block_size=bs, allow_raw=True)
                )
                methods[f"fipb_forced_bs{block_size}"] = (
                    lambda payload, bs=block_size: encode(payload, block_size=bs, allow_raw=False)
                )
            for method, function in methods.items():
                compressed, elapsed, peak = timed_call(
                    function,
                    data,
                    int(config["repetitions"]),
                    int(config["warmups"]),
                )
                if method.startswith("fipb_") and decode(compressed) != data:
                    raise RuntimeError(f"roundtrip failed for {path} with {method}")
                metrics = compression_metrics(len(data), len(compressed))
                row = {
                    "corpus": corpus,
                    "file": str(path.resolve().relative_to(ROOT.parent)),
                    "method": method,
                    "original_bytes": len(data),
                    "compressed_bytes": len(compressed),
                    "ratio": metrics["ratio"],
                    "saving_fraction": metrics["saving_fraction"],
                    "bits_per_byte": metrics["bits_per_byte"],
                    "entropy_bits_per_byte": entropy,
                    "gap_to_h0_bits_per_byte": metrics["bits_per_byte"] - entropy,
                    "median_seconds": elapsed,
                    "throughput_mib_s": (
                        len(data) / (1024 * 1024) / elapsed if elapsed else float("inf")
                    ),
                    "peak_tracemalloc_bytes": peak,
                }
                rows.append(row)
                writer.writerow(row)
                handle.flush()
                print(corpus, path.name, method, f"ratio={metrics['ratio']:.4f}", flush=True)
    finally:
        handle.close()
    environment = {
        "python": sys.version,
        "platform": platform.platform(),
        "processor": platform.processor(),
        "config": config,
    }
    (ROOT / "results" / "environment.json").write_text(
        json.dumps(environment, indent=2), encoding="utf-8"
    )
    print(f"Wrote {len(rows)} rows to {output}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--config",
        type=Path,
        default=ROOT / "config" / "experiment.json",
    )
    args = parser.parse_args()
    main(args.config)
