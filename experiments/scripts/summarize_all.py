from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
REPORTS = ROOT / "reports"
FIGURES = ROOT / "figures"
SEED = 20260608


def bootstrap_mean(values: np.ndarray, iterations: int = 10_000) -> tuple[float, float]:
    if len(values) == 1:
        return float(values[0]), float(values[0])
    rng = np.random.default_rng(SEED)
    draws = rng.choice(values, size=(iterations, len(values)), replace=True).mean(axis=1)
    return tuple(np.quantile(draws, [0.025, 0.975]))


def summarize_campaign(path: Path) -> pd.DataFrame:
    frame = pd.read_csv(path)
    rows = []
    for (corpus, method), group in frame.groupby(["corpus", "method"]):
        low, high = bootstrap_mean(group["ratio"].to_numpy(float))
        rows.append(
            {
                "campaign": path.stem,
                "corpus": corpus,
                "method": method,
                "files": group["file"].nunique(),
                "mean_ratio": group["ratio"].mean(),
                "median_ratio": group["ratio"].median(),
                "weighted_ratio": group["compressed_bytes"].sum()
                / group["original_bytes"].sum(),
                "ci95_mean_low": low,
                "ci95_mean_high": high,
                "mean_throughput_mib_s": group["throughput_mib_s"].mean(),
            }
        )
    return pd.DataFrame(rows)


def main() -> None:
    FIGURES.mkdir(parents=True, exist_ok=True)
    campaign_paths = [
        RESULTS / "benchmark.csv",
        RESULTS / "benchmark_canterbury.csv",
        RESULTS / "benchmark_silesia_sample.csv",
    ]
    summaries = pd.concat(
        [summarize_campaign(path) for path in campaign_paths if path.exists()],
        ignore_index=True,
    )
    summaries.to_csv(RESULTS / "campaign_summary.csv", index=False)

    ablation = pd.read_csv(RESULTS / "ablation.csv")
    ablation_summary = (
        ablation.groupby(["corpus", "block_size"], as_index=False)
        .agg(
            mean_index_ratio=("index_ratio", "mean"),
            mean_gap_ratio=("gap_ratio", "mean"),
            mean_complete_payload_ratio=("complete_payload_ratio", "mean"),
        )
    )
    ablation_summary.to_csv(RESULTS / "ablation_summary.csv", index=False)

    full = pd.read_csv(RESULTS / "full_baselines.csv")
    full_summary = (
        full.groupby(["corpus", "method"], as_index=False)
        .agg(
            mean_ratio=("ratio", "mean"),
            median_ratio=("ratio", "median"),
            weighted_ratio=(
                "compressed_bytes",
                lambda values: values.sum()
                / full.loc[values.index, "original_bytes"].sum(),
            ),
            mean_throughput_mib_s=("throughput_mib_s", "mean"),
        )
        .sort_values(["corpus", "weighted_ratio"])
    )
    full_summary.to_csv(RESULTS / "full_baselines_summary.csv", index=False)

    canterbury = pd.read_csv(RESULTS / "benchmark_canterbury.csv")
    fib = canterbury[canterbury["method"].str.startswith("fipb_")]
    per_file_oracle = fib.groupby("file")["ratio"].min()
    modern = canterbury[
        canterbury["method"].isin(["zlib_9", "bzip2_9", "lzma_9", "brotli_11"])
    ]
    modern_oracle = modern.groupby("file")["ratio"].min()
    paired = pd.DataFrame(
        {"best_fipb": per_file_oracle, "best_modern": modern_oracle}
    ).dropna()
    paired["factor_vs_modern"] = paired["best_fipb"] / paired["best_modern"]
    paired.to_csv(RESULTS / "canterbury_oracle_comparison.csv")

    plot = ablation_summary[ablation_summary["corpus"] == "canterbury"]
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.plot(plot["block_size"], plot["mean_index_ratio"], marker="o", label="Indices")
    ax.plot(plot["block_size"], plot["mean_gap_ratio"], marker="o", label="Reduced gaps")
    ax.plot(
        plot["block_size"],
        plot["mean_complete_payload_ratio"],
        marker="o",
        label="Serialized payload",
    )
    ax.axhline(1.0, color="black", linestyle="--", linewidth=1)
    ax.set_xscale("log", base=2)
    ax.set_xlabel("Block size (bytes)")
    ax.set_ylabel("Mean size / original size")
    ax.set_title("Canterbury ablation")
    ax.legend()
    fig.tight_layout()
    fig.savefig(FIGURES / "canterbury_ablation.pdf")
    fig.savefig(FIGURES / "canterbury_ablation.png", dpi=200)
    plt.close(fig)

    integer_report = (REPORTS / "04_integer_viability.md").read_text(encoding="utf-8")
    key = {
        "canterbury_best_fipb_mean": float(per_file_oracle.mean()),
        "canterbury_best_modern_mean": float(modern_oracle.mean()),
        "canterbury_median_factor_vs_modern": float(
            paired["factor_vs_modern"].median()
        ),
        "canterbury_fipb_wins_over_raw_files": int((per_file_oracle < 1).sum()),
        "canterbury_files": int(len(per_file_oracle)),
        "forced_fipb_wins_over_raw_files": int(
            (
                canterbury[canterbury["method"].str.startswith("fipb_forced")]
                .groupby("file")["ratio"]
                .min()
                < 1
            ).sum()
        ),
    }
    (RESULTS / "key_findings.json").write_text(
        json.dumps(key, indent=2), encoding="utf-8"
    )

    report = f"""# Consolidated Experimental Findings

## Integer viability

{integer_report.splitlines()[4]}
{integer_report.splitlines()[5]}
{integer_report.splitlines()[6]}
{integer_report.splitlines()[7]}

## Canterbury

- Best FIPB configuration per file has mean ratio `{key['canterbury_best_fipb_mean']:.4f}`.
- Best modern baseline per file has mean ratio `{key['canterbury_best_modern_mean']:.4f}`.
- FIPB's median size is `{key['canterbury_median_factor_vs_modern']:.2f}x` the
  best modern codec size.
- A FIPB configuration beats raw storage on
  `{key['canterbury_fipb_wins_over_raw_files']}/{key['canterbury_files']}` files.
- Forced Fibonacci beats raw storage on
  `{key['forced_fipb_wins_over_raw_files']}/{key['canterbury_files']}` files.

## Interpretation

The reduced-gap transform sometimes shortens the optimistic representation,
but complete serialization confines that effect to a narrow regime. The
scientific contribution is a complete-cost evaluation framework for amortized
positional transforms, calibrated with Fibonacci, alternative bases, and
zero-structure controls.
"""
    (REPORTS / "07_08_consolidated_findings.md").write_text(
        report, encoding="utf-8"
    )
    print(report)


if __name__ == "__main__":
    main()
