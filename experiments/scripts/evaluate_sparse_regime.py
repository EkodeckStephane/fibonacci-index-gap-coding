from __future__ import annotations

import csv
import random
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from fibcodec.baselines import CODECS
from fibcodec.metrics import shannon_entropy

BUILD = ROOT / "native" / "java" / "build"
SOURCE = ROOT / "native" / "java" / "FisaBenchmark.java"
DATA = ROOT / "data" / "sparse_regime"


def generate(size: int = 1_048_576, seed: int = 20260609) -> list[Path]:
    DATA.mkdir(parents=True, exist_ok=True)
    paths = []
    for density in (1, 5, 10, 25, 50, 75, 100):
        rng = random.Random(seed + density)
        probability = density / 100
        data = bytearray(size)
        for index in range(size):
            if rng.random() < probability:
                data[index] = rng.randint(1, 255)
        path = DATA / f"random_nonzero_{density:03d}.bin"
        path.write_bytes(data)
        paths.append(path)
    return paths


def native_fisa(path: Path) -> tuple[int, float, float]:
    process = subprocess.run(
        [
            "java",
            "-Xmx4g",
            "-cp",
            str(BUILD),
            "FisaBenchmark",
            str(path),
            "256",
            "0",
        ],
        check=True,
        text=True,
        capture_output=True,
    )
    values = next(csv.DictReader(process.stdout.splitlines()))
    return (
        int(values["encoded_bytes"]),
        float(values["encode_seconds"]),
        float(values["decode_seconds"]),
    )


def main() -> None:
    BUILD.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        ["javac", "--release", "8", "-d", str(BUILD), str(SOURCE)],
        check=True,
    )
    rows = []
    for path in generate():
        data = path.read_bytes()
        density = int(path.stem.rsplit("_", 1)[1]) / 100
        h0 = shannon_entropy(data)
        encoded, encode_seconds, decode_seconds = native_fisa(path)
        rows.append(
            {
                "density": density,
                "method": "fisa_native",
                "original_bytes": len(data),
                "encoded_bytes": encoded,
                "ratio": encoded / len(data),
                "entropy_bits_per_byte": h0,
                "seconds": encode_seconds,
                "throughput_mib_s": len(data) / 1048576 / encode_seconds,
            }
        )
        for name, function in CODECS.items():
            if name in {"raw", "rle"}:
                continue
            start = time.perf_counter()
            payload = function(data)
            elapsed = time.perf_counter() - start
            rows.append(
                {
                    "density": density,
                    "method": name,
                    "original_bytes": len(data),
                    "encoded_bytes": len(payload),
                    "ratio": len(payload) / len(data),
                    "entropy_bits_per_byte": h0,
                    "seconds": elapsed,
                    "throughput_mib_s": len(data) / 1048576 / elapsed,
                }
            )
        print(path.name, f"h0={h0:.4f}", flush=True)

    output = ROOT / "results" / "sparse_regime.csv"
    with output.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)

    import pandas as pd

    frame = pd.DataFrame(rows)
    pivot = frame.pivot(index="density", columns="method", values="ratio")
    report = [
        "# Controlled Sparse-Byte Regime",
        "",
        "Each 1 MiB file contains independently positioned non-zero bytes with",
        "uniform values in `1..255`; all remaining bytes are zero. The generator",
        "uses fixed seed `20260609 + density_percent`.",
        "",
        "## Complete-stream ratios",
        "",
        pivot.to_markdown(floatfmt=".6f"),
        "",
        "This experiment tests whether zero dominance alone provides a",
        "competitive application regime. It does not use domain labels or",
        "select files after observing codec performance.",
        "",
    ]
    (ROOT / "reports" / "18_sparse_regime.md").write_text(
        "\n".join(report), encoding="utf-8"
    )
    print(pivot.to_string())


if __name__ == "__main__":
    main()
