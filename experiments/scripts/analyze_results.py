from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
CSV = ROOT / "results" / "benchmark.csv"


def main() -> None:
    frame = pd.read_csv(CSV)
    results = ROOT / "results"
    figures = ROOT / "figures"
    reports = ROOT / "reports"
    figures.mkdir(parents=True, exist_ok=True)

    summary = (
        frame.groupby(["corpus", "method"], as_index=False)
        .agg(
            mean_ratio=("ratio", "mean"),
            median_ratio=("ratio", "median"),
            mean_throughput_mib_s=("throughput_mib_s", "mean"),
            median_peak_bytes=("peak_tracemalloc_bytes", "median"),
            mean_gap_to_h0_bpb=("gap_to_h0_bits_per_byte", "mean"),
            files=("file", "nunique"),
        )
        .sort_values(["corpus", "mean_ratio"])
    )
    summary.to_csv(results / "summary.csv", index=False)

    synthetic = summary[summary["corpus"] == "synthetic"].head(18)
    fig, ax = plt.subplots(figsize=(11, 6))
    ax.barh(synthetic["method"], synthetic["mean_ratio"])
    ax.axvline(1.0, color="black", linewidth=1, linestyle="--")
    ax.set_xlabel("Mean compressed/original size ratio (lower is better)")
    ax.set_title("Synthetic corpus: complete serialized size")
    fig.tight_layout()
    fig.savefig(figures / "synthetic_mean_ratio.pdf")
    fig.savefig(figures / "synthetic_mean_ratio.png", dpi=200)
    plt.close(fig)

    best = summary.groupby("corpus").first().reset_index()
    report = [
        "# Benchmark Summary",
        "",
        "All ratios include complete serialized output.",
        "",
    ]
    for row in best.itertuples():
        report.append(
            f"- `{row.corpus}`: best mean ratio `{row.mean_ratio:.4f}` "
            f"from `{row.method}` over {row.files} files."
        )
    report.extend(
        [
            "",
            "Detailed per-file measurements are in `results/benchmark.csv`; "
            "aggregates are in `results/summary.csv`.",
        ]
    )
    (reports / "07_08_benchmark_and_entropy.md").write_text(
        "\n".join(report) + "\n", encoding="utf-8"
    )
    print(summary.to_string(index=False))


if __name__ == "__main__":
    main()
