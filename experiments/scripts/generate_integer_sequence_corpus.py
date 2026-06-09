from __future__ import annotations

import csv
import random
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "data" / "integer_sequences"
SEED = 20260609


def geometric_gaps(rng: random.Random, count: int, probability: float) -> list[int]:
    gaps = []
    for _ in range(count):
        gap = 1
        while rng.random() > probability:
            gap += 1
        gaps.append(gap)
    return gaps


def cumulative(gaps: list[int]) -> list[int]:
    total = 0
    values = []
    for gap in gaps:
        total += gap
        values.append(total)
    return values


def main() -> None:
    OUTPUT.mkdir(parents=True, exist_ok=True)
    rng = random.Random(SEED)
    datasets = {
        "dense": list(range(0, 100_000)),
        "geometric_p50": cumulative(geometric_gaps(rng, 100_000, 0.50)),
        "geometric_p20": cumulative(geometric_gaps(rng, 100_000, 0.20)),
        "posting_like": cumulative(
            [
                1 + int(rng.paretovariate(1.7))
                for _ in range(100_000)
            ]
        ),
        "quadratic": [index * index for index in range(100_000)],
    }
    rows = []
    for name, values in datasets.items():
        path = OUTPUT / f"{name}.txt"
        path.write_text("\n".join(map(str, values)) + "\n", encoding="ascii")
        rows.append(
            {
                "name": name,
                "count": len(values),
                "maximum": values[-1] if values else 0,
                "seed": SEED,
            }
        )
    with (OUTPUT / "manifest.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)
    print(f"Wrote {len(rows)} integer-sequence datasets to {OUTPUT}")


if __name__ == "__main__":
    main()
