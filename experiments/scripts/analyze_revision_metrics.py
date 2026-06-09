from __future__ import annotations

from pathlib import Path

import pandas as pd
from scipy.stats import wilcoxon

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"


def threshold_summary(native: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for corpus, group in native[native["corpus"].isin(["canterbury", "silesia"])].groupby(
        "corpus", sort=False
    ):
        full_blocks = int(group["full_blocks"].sum())
        threshold_blocks = int(group["k_star_blocks"].sum())
        all_blocks = int((group["full_blocks"] + (group["original_bytes"] % 256 != 0)).sum())
        shared_blocks = int(group["shared_blocks"].sum())
        rows.append(
            {
                "corpus": corpus,
                "files": len(group),
                "k_star_min": int(group["k_star"].min()),
                "k_star_median": float(group["k_star"].median()),
                "k_star_max": int(group["k_star"].max()),
                "full_blocks": full_blocks,
                "k_star_blocks": threshold_blocks,
                "k_star_fraction": threshold_blocks / full_blocks,
                "all_blocks": all_blocks,
                "shared_blocks": shared_blocks,
                "shared_block_fraction": shared_blocks / all_blocks,
            }
        )
    return pd.DataFrame(rows)


def full_paired_statistics(native: pd.DataFrame, baselines: pd.DataFrame) -> pd.DataFrame:
    rows = []
    modern_methods = ["zlib_9", "bzip2_9", "lzma_9", "brotli_11", "zstd_19", "ppmd_6"]
    for corpus in ("canterbury", "silesia"):
        fisa = native[native["corpus"] == corpus].set_index("file")["ratio"]
        modern = (
            baselines[
                (baselines["corpus"] == corpus)
                & baselines["method"].isin(modern_methods)
            ]
            .groupby("file")["ratio"]
            .min()
        )
        paired = pd.concat(
            [fisa.rename("fisa_ratio"), modern.rename("best_modern_ratio")], axis=1
        ).dropna()
        differences = paired["fisa_ratio"] - paired["best_modern_ratio"]
        test = wilcoxon(differences, alternative="greater", zero_method="wilcox")
        rows.append(
            {
                "corpus": corpus,
                "files": len(paired),
                "mean_fisa_ratio": paired["fisa_ratio"].mean(),
                "mean_best_modern_ratio": paired["best_modern_ratio"].mean(),
                "median_ratio_factor": (
                    paired["fisa_ratio"] / paired["best_modern_ratio"]
                ).median(),
                "fisa_wins": int((differences < 0).sum()),
                "ties": int((differences == 0).sum()),
                "modern_wins": int((differences > 0).sum()),
                "wilcoxon_statistic": float(test.statistic),
                "one_sided_p_value": float(test.pvalue),
            }
        )
    return pd.DataFrame(rows)


def throughput_comparison(
    native: pd.DataFrame, baselines: pd.DataFrame
) -> pd.DataFrame:
    rows = []
    selected = ["fisa_1_0", "zlib_9", "zstd_19", "brotli_11", "lzma_9", "ppmd_6"]
    for corpus in ("canterbury", "silesia"):
        fisa = native[native["corpus"] == corpus]
        rows.append(
            {
                "corpus": corpus,
                "method": "fisa_1_0",
                "weighted_ratio": fisa["encoded_bytes"].sum()
                / fisa["original_bytes"].sum(),
                "aggregate_encode_mib_s": fisa["original_bytes"].sum()
                / 1048576
                / fisa["encode_seconds"].sum(),
            }
        )
        for method in selected[1:]:
            group = baselines[
                (baselines["corpus"] == corpus) & (baselines["method"] == method)
            ]
            rows.append(
                {
                    "corpus": corpus,
                    "method": method,
                    "weighted_ratio": group["compressed_bytes"].sum()
                    / group["original_bytes"].sum(),
                    "aggregate_encode_mib_s": group["original_bytes"].sum()
                    / 1048576
                    / group["seconds"].sum(),
                }
            )
    return pd.DataFrame(rows)


def prefix_full_comparison(native: pd.DataFrame) -> pd.DataFrame:
    exploratory = pd.read_csv(RESULTS / "advanced_gap_codes.csv")
    prefixes = exploratory[
        (exploratory["corpus"] == "silesia_sample")
        & (exploratory["method"] == "shared_alphabet_hybrid")
    ].set_index("file")["ratio"]
    complete = native[native["corpus"] == "silesia"].set_index("file")["ratio"]
    frame = pd.concat(
        [prefixes.rename("prefix_ratio"), complete.rename("complete_ratio")], axis=1
    ).dropna()
    frame["absolute_change"] = frame["complete_ratio"] - frame["prefix_ratio"]
    frame["complete_to_prefix_factor"] = (
        frame["complete_ratio"] / frame["prefix_ratio"]
    )
    return frame.reset_index()


def main() -> None:
    native = pd.read_csv(RESULTS / "native_fisa.csv")
    baselines = pd.read_csv(RESULTS / "full_baselines.csv")

    threshold = threshold_summary(native)
    paired = full_paired_statistics(native, baselines)
    throughput = throughput_comparison(native, baselines)
    prefix_full = prefix_full_comparison(native)

    threshold.to_csv(RESULTS / "k_star_validation.csv", index=False)
    paired.to_csv(RESULTS / "full_paired_statistics.csv", index=False)
    throughput.to_csv(RESULTS / "throughput_comparison.csv", index=False)
    prefix_full.to_csv(RESULTS / "prefix_full_comparison.csv", index=False)

    report = [
        "# Revision Metrics",
        "",
        "## Empirical calibration of the sufficient term threshold",
        "",
        threshold.to_markdown(index=False, floatfmt=".6f"),
        "",
        "The threshold is file-specific because each FISA file has its own shared",
        "alphabet and amortized metadata. Fractions count complete 256-byte blocks.",
        "",
        "## Complete-file paired statistics",
        "",
        paired.to_markdown(index=False, floatfmt=".6f"),
        "",
        "## Aggregate encoding throughput",
        "",
        throughput.to_markdown(index=False, floatfmt=".6f"),
        "",
        "FISA uses the Java implementation. Baselines use their Python bindings on",
        "the same machine and include the configured high-compression settings.",
        "",
        "## Fixed-prefix versus complete-file ratios",
        "",
        prefix_full.to_markdown(index=False, floatfmt=".6f"),
        "",
    ]
    (ROOT / "reports" / "21_revision_metrics.md").write_text(
        "\n".join(report), encoding="utf-8"
    )
    print("\n".join(report))


if __name__ == "__main__":
    main()
