from __future__ import annotations

import csv
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from fibcodec.transform import reduce_indices, zeckendorf_indices


def representation_bits(value: int) -> int:
    gaps = reduce_indices(zeckendorf_indices(value))
    return sum(max(1, gap.bit_length()) for gap in gaps)


def main(limit: int = 1_000_000) -> None:
    output = ROOT / "results" / "integer_viability.csv"
    output.parent.mkdir(parents=True, exist_ok=True)
    counts = {"gain": 0, "equal": 0, "expansion": 0}
    total_gain = 0
    worst = (0, 0)
    best = (0, 0)
    with output.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=["value", "binary_bits", "gap_bits", "gain_bits", "class"],
        )
        writer.writeheader()
        for value in range(1, limit + 1):
            binary_bits = value.bit_length()
            gap_bits = representation_bits(value)
            gain = binary_bits - gap_bits
            label = "gain" if gain > 0 else "equal" if gain == 0 else "expansion"
            counts[label] += 1
            total_gain += gain
            if gain < worst[1]:
                worst = (value, gain)
            if gain > best[1]:
                best = (value, gain)
            writer.writerow(
                {
                    "value": value,
                    "binary_bits": binary_bits,
                    "gap_bits": gap_bits,
                    "gain_bits": gain,
                    "class": label,
                }
            )
    summary = ROOT / "reports" / "04_integer_viability.md"
    summary.write_text(
        "# Exhaustive Integer Viability\n\n"
        f"Range: `1..{limit:,}`.\n\n"
        f"- Gain: {counts['gain']:,} ({counts['gain']/limit:.2%})\n"
        f"- Equal: {counts['equal']:,} ({counts['equal']/limit:.2%})\n"
        f"- Expansion: {counts['expansion']:,} ({counts['expansion']/limit:.2%})\n"
        f"- Mean raw gap-representation gain: {total_gain/limit:.4f} bits/value\n"
        f"- Best observed: d={best[0]}, gain={best[1]} bits\n"
        f"- Worst observed: d={worst[0]}, gain={worst[1]} bits\n\n"
        "This comparison excludes container metadata and therefore represents an "
        "optimistic upper bound for the proposed representation.\n",
        encoding="utf-8",
    )
    print(summary.read_text(encoding="utf-8"))


if __name__ == "__main__":
    selected_limit = int(sys.argv[1]) if len(sys.argv) > 1 else 1_000_000
    main(selected_limit)

