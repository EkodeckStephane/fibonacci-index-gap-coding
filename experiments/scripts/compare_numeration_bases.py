from __future__ import annotations

import argparse
import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def sequence_up_to(limit: int, seeds: tuple[int, int]) -> list[int]:
    values = [seeds[0], seeds[1]]
    while values[-1] <= limit:
        values.append(values[-1] + values[-2])
    return values[:-1]


def greedy_indices(value: int, sequence: list[int], index_offset: int) -> list[int]:
    indices: list[int] = []
    remainder = value
    index = len(sequence) - 1
    while remainder:
        while sequence[index] > remainder:
            index -= 1
        indices.append(index + index_offset)
        remainder -= sequence[index]
    return indices


def binary_indices(value: int) -> list[int]:
    return [
        index
        for index in range(value.bit_length() - 1, -1, -1)
        if value & (1 << index)
    ]


def gap_bits(indices: list[int]) -> int:
    if not indices:
        return 0
    gaps = [
        indices[index] - indices[index + 1]
        for index in range(len(indices) - 1)
    ] + [indices[-1]]
    return sum(max(1, gap.bit_length()) for gap in gaps)


def main(limit: int) -> None:
    fibonacci = sequence_up_to(limit, (1, 2))
    lucas = sequence_up_to(limit, (1, 3))
    totals = {
        "fibonacci": {"gain": 0, "equal": 0, "expansion": 0, "bits": 0, "terms": 0},
        "lucas_greedy": {"gain": 0, "equal": 0, "expansion": 0, "bits": 0, "terms": 0},
        "binary_sparse": {"gain": 0, "equal": 0, "expansion": 0, "bits": 0, "terms": 0},
    }
    wins = {name: 0 for name in totals}
    ties = 0

    for value in range(1, limit + 1):
        representations = {
            "fibonacci": greedy_indices(value, fibonacci, 2),
            "lucas_greedy": greedy_indices(value, lucas, 1),
            "binary_sparse": binary_indices(value),
        }
        measured = {}
        direct = value.bit_length()
        for name, indices in representations.items():
            bits = gap_bits(indices)
            measured[name] = bits
            gain = direct - bits
            label = "gain" if gain > 0 else "equal" if gain == 0 else "expansion"
            totals[name][label] += 1
            totals[name]["bits"] += bits
            totals[name]["terms"] += len(indices)
        best = min(measured.values())
        best_names = [name for name, bits in measured.items() if bits == best]
        if len(best_names) == 1:
            wins[best_names[0]] += 1
        else:
            ties += 1

    rows = []
    for name, values in totals.items():
        rows.append(
            {
                "method": name,
                "limit": limit,
                "gain_fraction": values["gain"] / limit,
                "equal_fraction": values["equal"] / limit,
                "expansion_fraction": values["expansion"] / limit,
                "mean_gap_bits": values["bits"] / limit,
                "mean_terms": values["terms"] / limit,
                "unique_best_fraction": wins[name] / limit,
            }
        )

    output = ROOT / "results" / "numeration_base_comparison.csv"
    with output.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)

    report = [
        "# Numeration-Basis Comparison",
        "",
        f"Exhaustive range: `1..{limit:,}`.",
        "",
        "All methods encode gaps between greedy term indices using the same",
        "optimistic sum of individual gap bit lengths. Container metadata is",
        "excluded. Fibonacci uses the canonical Zeckendorf basis `(1, 2, ...)`.",
        "Lucas uses the greedy basis `(1, 3, 4, ...)`; unlike Zeckendorf, this",
        "representation is not claimed to be unique. Binary sparse coding uses",
        "the positions of set bits.",
        "",
        "| Method | Gain | Equal | Expansion | Mean gap bits | Mean terms | Unique best |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for row in rows:
        report.append(
            f"| {row['method']} "
            f"| {row['gain_fraction']:.2%} "
            f"| {row['equal_fraction']:.2%} "
            f"| {row['expansion_fraction']:.2%} "
            f"| {row['mean_gap_bits']:.4f} "
            f"| {row['mean_terms']:.4f} "
            f"| {row['unique_best_fraction']:.2%} |"
        )
    report.extend(
        [
            "",
            f"Cross-method ties for best optimistic length: {ties / limit:.2%}.",
            "",
        ]
    )
    path = ROOT / "reports" / "17_numeration_base_comparison.md"
    path.write_text("\n".join(report), encoding="utf-8")
    print(path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=1_000_000)
    args = parser.parse_args()
    main(args.limit)
