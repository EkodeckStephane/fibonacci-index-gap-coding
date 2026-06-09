from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from fibcodec.transform import reduce_indices, zeckendorf_indices


def representation_bits(value: int) -> int:
    gaps = reduce_indices(zeckendorf_indices(value))
    return sum(max(1, gap.bit_length()) for gap in gaps)


def classify(gain: int) -> int:
    return 0 if gain > 0 else 1 if gain == 0 else 2


def main(limit: int, checkpoints: list[int]) -> None:
    checkpoints = sorted({point for point in checkpoints if 0 < point <= limit})
    if not checkpoints or checkpoints[-1] != limit:
        checkpoints.append(limit)

    rows: list[dict[str, object]] = []
    cumulative_counts = [0, 0, 0]
    cumulative_gain = 0
    band_counts = [0, 0, 0]
    band_gain = 0
    band_start = 1
    checkpoint_set = set(checkpoints)

    for value in range(1, limit + 1):
        gain = value.bit_length() - representation_bits(value)
        label = classify(gain)
        cumulative_counts[label] += 1
        cumulative_gain += gain
        band_counts[label] += 1
        band_gain += gain

        if value not in checkpoint_set:
            continue

        cumulative_n = value
        band_n = value - band_start + 1
        for scope, start, count, total_gain in (
            ("cumulative", 1, cumulative_counts, cumulative_gain),
            ("band", band_start, band_counts, band_gain),
        ):
            n = cumulative_n if scope == "cumulative" else band_n
            rows.append(
                {
                    "scope": scope,
                    "start": start,
                    "end": value,
                    "count": n,
                    "gain_count": count[0],
                    "equal_count": count[1],
                    "expansion_count": count[2],
                    "gain_fraction": count[0] / n,
                    "equal_fraction": count[1] / n,
                    "expansion_fraction": count[2] / n,
                    "mean_gain_bits": total_gain / n,
                }
            )
        band_start = value + 1
        band_counts = [0, 0, 0]
        band_gain = 0

    output = ROOT / "results" / "integer_scaling.csv"
    with output.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)

    report = ROOT / "reports" / "04_integer_scaling.md"
    cumulative = [row for row in rows if row["scope"] == "cumulative"]
    lines = [
        "# Integer-Range Scaling",
        "",
        "The comparison is exhaustive at every integer up to the selected limit.",
        "It counts only the reduced-index representation and excludes all",
        "container metadata.",
        "",
        "| Range | Gain | Equal | Expansion | Mean gain (bits/value) |",
        "|---|---:|---:|---:|---:|",
    ]
    for row in cumulative:
        lines.append(
            f"| `1..{int(row['end']):,}` "
            f"| {float(row['gain_fraction']):.2%} "
            f"| {float(row['equal_fraction']):.2%} "
            f"| {float(row['expansion_fraction']):.2%} "
            f"| {float(row['mean_gain_bits']):.4f} |"
        )
    lines.extend(
        [
            "",
            "The increasing favorable fraction does not establish complete-stream",
            "compression because alphabet, length, framing, and padding costs are",
            "excluded.",
            "",
        ]
    )
    report.write_text("\n".join(lines), encoding="utf-8")
    print(report.read_text(encoding="utf-8"))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=10_000_000)
    parser.add_argument(
        "--checkpoints",
        type=int,
        nargs="*",
        default=[1_000_000, 2_000_000, 5_000_000, 10_000_000],
    )
    args = parser.parse_args()
    main(args.limit, args.checkpoints)
