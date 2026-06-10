from __future__ import annotations

import argparse
import csv
import math
import random
import statistics
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from fibcodec.transform import zeckendorf_indices


def main(samples: int, seed: int) -> None:
    phi = (1.0 + math.sqrt(5.0)) / 2.0
    coefficient = 1.0 / ((phi**2 + 1.0) * math.log2(phi))
    rng = random.Random(seed)
    rows: list[dict[str, object]] = []

    for block_bytes in (16, 32, 64, 128, 256):
        bits = 8 * block_bytes
        counts = []
        for _ in range(samples):
            value = rng.getrandbits(bits - 1) | (1 << (bits - 1))
            counts.append(len(zeckendorf_indices(value)))
        rows.append(
            {
                "block_bytes": block_bytes,
                "bits": bits,
                "samples": samples,
                "asymptotic_mean_terms": coefficient * bits,
                "simulated_mean_terms": statistics.mean(counts),
                "simulated_std_terms": statistics.pstdev(counts),
                "simulated_min_terms": min(counts),
                "simulated_max_terms": max(counts),
                "at_most_326": sum(count <= 326 for count in counts),
                "at_most_392": sum(count <= 392 for count in counts),
            }
        )

    output = ROOT / "results" / "zeckendorf_term_scaling.csv"
    with output.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)

    report = ROOT / "reports" / "22_zeckendorf_term_scaling.md"
    lines = [
        "# Zeckendorf Term-Count Scaling",
        "",
        f"Seed: `{seed}`; exact-bit-length samples per row: `{samples}`.",
        "",
        "Lekkerkerker's theorem gives an average of "
        r"$n/(\varphi^2+1)+O(1)$ summands for integers in "
        r"$[F_n,F_{n+1})$. Since $n\sim \ell/\log_2\varphi$, the leading "
        f"coefficient for an ell-bit integer is `{coefficient:.6f}`.",
        "",
        "| Block | Bits | Asymptotic mean | Simulated mean | Std. dev. | Min--max | <=326 | <=392 |",
        "|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for row in rows:
        lines.append(
            f"| {row['block_bytes']} | {row['bits']} "
            f"| {float(row['asymptotic_mean_terms']):.2f} "
            f"| {float(row['simulated_mean_terms']):.2f} "
            f"| {float(row['simulated_std_terms']):.2f} "
            f"| {row['simulated_min_terms']}--{row['simulated_max_terms']} "
            f"| {row['at_most_326']}/{samples} "
            f"| {row['at_most_392']}/{samples} |"
        )
    lines.extend(
        [
            "",
            "The 256-byte simulation is the direct comparison for the measured",
            "complete-stream thresholds. No sampled generic 2048-bit integer",
            "falls below either threshold.",
            "",
        ]
    )
    report.write_text("\n".join(lines), encoding="utf-8")
    print(report.read_text(encoding="utf-8"))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--samples", type=int, default=5000)
    parser.add_argument("--seed", type=int, default=20260610)
    args = parser.parse_args()
    main(args.samples, args.seed)
